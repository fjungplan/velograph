from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import Optional, Dict

from app.models.edit import Edit, EditType, EditStatus
from app.models.user import User, UserRole
from app.models.team import TeamEra, TeamNode
from app.schemas.moderation import (
    PendingEditResponse,
    ReviewEditResponse,
    ModerationStatsResponse
)

class ModerationService:
    @staticmethod
    async def format_edit_for_review(
        session: AsyncSession,
        edit: Edit
    ) -> PendingEditResponse:
        user = await session.get(User, edit.user_id)
        target_info = {}
        if edit.edit_type == EditType.METADATA and edit.target_era_id:
            era = await session.get(TeamEra, edit.target_era_id)
            if era:
                target_info = {
                    'type': 'era',
                    'era_id': str(era.era_id),
                    'team_name': era.registered_name,
                    'year': era.season_year
                }
        elif edit.target_node_id:
            node = await session.get(TeamNode, edit.target_node_id)
            if node:
                target_info = {
                    'type': 'node',
                    'node_id': str(node.node_id),
                    'founding_year': node.founding_year
                }
        return PendingEditResponse(
            edit_id=str(edit.edit_id),
            edit_type=edit.edit_type.value,
            user_email=user.email,
            user_display_name=user.display_name,
            target_info=target_info,
            changes=edit.changes,
            reason=edit.reason,
            created_at=edit.created_at
        )

    @staticmethod
    async def review_edit(
        session: AsyncSession,
        edit: Edit,
        admin: User,
        approved: bool,
        notes: Optional[str] = None
    ) -> ReviewEditResponse:
        import logging
        logger = logging.getLogger("moderation")
        if approved:
            edit.status = EditStatus.APPROVED
            edit.reviewed_by = admin.user_id
            edit.reviewed_at = datetime.utcnow()
            edit.review_notes = notes
            try:
                if edit.edit_type == EditType.METADATA:
                    await ModerationService._apply_metadata_edit(session, edit)
                elif edit.edit_type == EditType.MERGE:
                    await ModerationService._apply_merge_edit(session, edit)
                elif edit.edit_type == EditType.SPLIT:
                    await ModerationService._apply_split_edit(session, edit)
                user = await session.get(User, edit.user_id)
                user.approved_edits_count += 1
                logger.info(f"Edit {edit.edit_id} approved by admin {admin.user_id}. User {user.user_id} now has {user.approved_edits_count} approvals.")
                if user.role == UserRole.NEW_USER and user.approved_edits_count >= 5:
                    user.role = UserRole.TRUSTED_USER
                    logger.info(f"User {user.user_id} promoted to Trusted User after {user.approved_edits_count} approvals.")
                    message = "Edit approved and user promoted to Trusted User"
                else:
                    message = "Edit approved and applied"
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to apply edit {edit.edit_id}: {str(e)}", exc_info=True)
                raise ValueError(f"Failed to apply edit: {str(e)}")
        else:
            edit.status = EditStatus.REJECTED
            edit.reviewed_by = admin.user_id
            edit.reviewed_at = datetime.utcnow()
            edit.review_notes = notes or "Edit rejected by moderator"
            logger.info(f"Edit {edit.edit_id} rejected by admin {admin.user_id}. Reason: {edit.review_notes}")
            message = "Edit rejected"
        await session.commit()
        return ReviewEditResponse(
            edit_id=str(edit.edit_id),
            status=edit.status.value,
            message=message
        )

    @staticmethod
    async def _apply_metadata_edit(session: AsyncSession, edit: Edit):
        era = await session.get(TeamEra, edit.target_era_id)
        if not era:
            raise ValueError("Target era not found")
        
        # Get the node if we need to update node-level fields
        node = None
        if edit.target_node_id:
            node = await session.get(TeamNode, edit.target_node_id)
            if not node:
                raise ValueError("Target node not found")
        
        changes = edit.changes
        
        # Apply era-level changes
        if 'registered_name' in changes:
            era.registered_name = changes['registered_name']
        if 'uci_code' in changes:
            era.uci_code = changes['uci_code']
        if 'tier_level' in changes:
            era.tier_level = changes['tier_level']
        
        # Apply node-level changes
        if node:
            if 'founding_year' in changes:
                node.founding_year = changes['founding_year']
            if 'dissolution_year' in changes:
                node.dissolution_year = changes['dissolution_year']
            node.updated_at = datetime.utcnow()
        
        era.is_manual_override = True
        era.source_origin = f"user_{edit.user_id}"
        era.updated_at = datetime.utcnow()
        await session.commit()
        # Logging for metadata edit application
        import logging
        logger = logging.getLogger("moderation")
        logger.info(f"Metadata edit {edit.edit_id} applied to era {era.era_id} and node {node.node_id if node else 'N/A'} by user {edit.user_id}")

    @staticmethod
    async def _apply_merge_edit(session: AsyncSession, edit: Edit):
        from app.services.edit_service import EditService
        from app.schemas.edits import MergeEventRequest
        changes = edit.changes
        request = MergeEventRequest(
            source_node_ids=changes['source_node_ids'],
            merge_year=changes['merge_year'],
            new_team_name=changes['new_team_name'],
            new_team_tier=changes['new_team_tier'],
            reason=edit.reason
        )
        user = await session.get(User, edit.user_id)
        await EditService._apply_merge(session, request, user)

    @staticmethod
    async def _apply_split_edit(session: AsyncSession, edit: Edit):
        from app.services.edit_service import EditService
        from app.schemas.edits import SplitEventRequest, NewTeamInfo
        changes = edit.changes
        request = SplitEventRequest(
            source_node_id=str(edit.target_node_id),
            split_year=changes['split_year'],
            new_teams=[
                NewTeamInfo(name=team['name'], tier=team['tier'])
                for team in changes['new_teams']
            ],
            reason=edit.reason
        )
        user = await session.get(User, edit.user_id)
        await EditService._apply_split(session, request, user)

    @staticmethod
    async def get_stats(session: AsyncSession) -> ModerationStatsResponse:
        pending_stmt = select(func.count(Edit.edit_id)).where(
            Edit.status == EditStatus.PENDING
        )
        pending_result = await session.execute(pending_stmt)
        pending_count = pending_result.scalar()
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        approved_today_stmt = select(func.count(Edit.edit_id)).where(
            and_(
                Edit.status == EditStatus.APPROVED,
                Edit.reviewed_at >= today_start
            )
        )
        approved_result = await session.execute(approved_today_stmt)
        approved_today = approved_result.scalar()
        rejected_today_stmt = select(func.count(Edit.edit_id)).where(
            and_(
                Edit.status == EditStatus.REJECTED,
                Edit.reviewed_at >= today_start
            )
        )
        rejected_result = await session.execute(rejected_today_stmt)
        rejected_today = rejected_result.scalar()
        pending_by_type_stmt = select(
            Edit.edit_type,
            func.count(Edit.edit_id)
        ).where(
            Edit.status == EditStatus.PENDING
        ).group_by(Edit.edit_type)
        type_result = await session.execute(pending_by_type_stmt)
        pending_by_type = {
            edit_type.value: count
            for edit_type, count in type_result.all()
        }
        return ModerationStatsResponse(
            pending_count=pending_count,
            approved_today=approved_today,
            rejected_today=rejected_today,
            pending_by_type=pending_by_type
        )
