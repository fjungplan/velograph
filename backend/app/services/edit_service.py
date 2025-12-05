from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import Dict
from uuid import UUID

from app.models.edit import Edit, EditType, EditStatus
from app.models.team import TeamEra, TeamNode
from app.models.lineage import LineageEvent
from app.models.enums import EventType
from app.models.user import User, UserRole
from app.schemas.edits import EditMetadataRequest, EditMetadataResponse, MergeEventRequest, SplitEventRequest


class EditService:
    @staticmethod
    async def create_metadata_edit(
        session: AsyncSession,
        user: User,
        request: EditMetadataRequest
    ) -> EditMetadataResponse:
        """Create a metadata edit (may be auto-approved for trusted users)"""
        # Get the target era
        try:
            era_id = UUID(request.era_id)
        except (ValueError, AttributeError):
            raise ValueError("Invalid era_id format")
        
        era = await session.get(TeamEra, era_id)
        if not era:
            raise ValueError("Era not found")
        
        # Build changes dict (only include fields that are being changed)
        changes = {}
        if request.registered_name:
            changes['registered_name'] = request.registered_name
        if request.uci_code:
            changes['uci_code'] = request.uci_code
        if request.tier_level:
            changes['tier_level'] = request.tier_level
        
        if not changes:
            raise ValueError("No changes specified")
        
        # Create edit record
        edit = Edit(
            user_id=user.user_id,
            edit_type=EditType.METADATA,
            target_era_id=era_id,
            changes=changes,
            reason=request.reason
        )
        
        # Auto-approve for trusted users and admins
        if user.role in [UserRole.TRUSTED_USER, UserRole.ADMIN]:
            edit.status = EditStatus.APPROVED
            edit.reviewed_by = user.user_id
            edit.reviewed_at = datetime.utcnow()
            
            # Apply changes immediately
            await EditService._apply_metadata_changes(session, era, changes, user)
            
            # Increment approved edits count
            user.approved_edits_count += 1
            
            message = "Edit approved and applied immediately"
        else:
            edit.status = EditStatus.PENDING
            message = "Edit submitted for moderation"
        
        session.add(edit)
        await session.commit()
        await session.refresh(edit)
        
        return EditMetadataResponse(
            edit_id=str(edit.edit_id),
            status=edit.status.value,
            message=message
        )
    
    @staticmethod
    async def _apply_metadata_changes(
        session: AsyncSession,
        era: TeamEra,
        changes: Dict,
        user: User
    ):
        """Apply metadata changes to an era"""
        if 'registered_name' in changes:
            era.registered_name = changes['registered_name']
        if 'uci_code' in changes:
            era.uci_code = changes['uci_code']
        if 'tier_level' in changes:
            era.tier_level = changes['tier_level']
        
        # Mark as manual override to prevent scraper from overwriting
        era.is_manual_override = True
        era.source_origin = f"user_{user.user_id}"
        era.updated_at = datetime.utcnow()
        
        await session.commit()
    
    @staticmethod
    async def create_merge_edit(
        session: AsyncSession,
        user: User,
        request: MergeEventRequest
    ) -> EditMetadataResponse:
        """
        Create a merge event edit.
        
        Args:
            session: Database session
            user: User creating the merge
            request: Merge request with source nodes and new team details
            
        Returns:
            EditMetadataResponse with edit_id, status, and message
            
        Raises:
            ValueError: If validation fails (invalid UUIDs, missing teams, inactive teams)
        """
        # Validate source nodes exist
        source_nodes = []
        for node_id_str in request.source_node_ids:
            try:
                node_id = UUID(node_id_str)
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid node_id format: {node_id_str}")
            
            # Eager-load eras relationship to avoid lazy loading in async context
            stmt = select(TeamNode).where(TeamNode.node_id == node_id).options(selectinload(TeamNode.eras))
            result = await session.execute(stmt)
            node = result.scalar_one_or_none()
            
            if not node:
                raise ValueError(f"Team node {node_id_str} not found")
            
            # Check node is active in merge year
            has_era = any(era.season_year == request.merge_year for era in node.eras)
            if not has_era:
                raise ValueError(f"Team {node_id_str} was not active in {request.merge_year}")
            
            source_nodes.append(node)
        
        # Create edit record
        edit = Edit(
            user_id=user.user_id,
            edit_type=EditType.MERGE,
            changes={
                'source_node_ids': request.source_node_ids,
                'merge_year': request.merge_year,
                'new_team_name': request.new_team_name,
                'new_team_tier': request.new_team_tier
            },
            reason=request.reason
        )
        
        # Auto-approve for trusted users and admins
        if user.role in [UserRole.TRUSTED_USER, UserRole.ADMIN]:
            edit.status = EditStatus.APPROVED
            edit.reviewed_by = user.user_id
            edit.reviewed_at = datetime.utcnow()
            
            # Apply merge immediately with validated nodes
            await EditService._apply_merge(session, request, user, source_nodes)
            
            user.approved_edits_count += 1
            message = "Merge created successfully"
        else:
            edit.status = EditStatus.PENDING
            message = "Merge submitted for moderation"
        
        session.add(edit)
        await session.commit()
        await session.refresh(edit)
        
        return EditMetadataResponse(
            edit_id=str(edit.edit_id),
            status=edit.status.value,
            message=message
        )
    
    @staticmethod
    async def _apply_merge(
        session: AsyncSession,
        request: MergeEventRequest,
        user: User,
        validated_source_nodes: list[TeamNode]
    ):
        """Apply a merge: close old nodes, create new node with links"""
        # Create new team node
        new_node = TeamNode(
            founding_year=request.merge_year
        )
        session.add(new_node)
        await session.flush()  # Get node_id
        
        # Create first era for new team
        new_era = TeamEra(
            node_id=new_node.node_id,
            season_year=request.merge_year,
            registered_name=request.new_team_name,
            tier_level=request.new_team_tier,
            source_origin=f"user_{user.user_id}",
            is_manual_override=True
        )
        session.add(new_era)
        
        # Close source nodes and create lineage links using validated nodes
        for source_node in validated_source_nodes:
            # Set dissolution year
            source_node.dissolution_year = request.merge_year
            source_node.updated_at = datetime.utcnow()
            
            # Create MERGE lineage event
            lineage_event = LineageEvent(
                previous_node_id=source_node.node_id,
                next_node_id=new_node.node_id,
                event_year=request.merge_year,
                event_type=EventType.MERGE,
                notes=f"Merged into {request.new_team_name}"
            )
            session.add(lineage_event)
        
        await session.commit()
    
    @staticmethod
    async def create_split_edit(
        session: AsyncSession,
        user: User,
        request: SplitEventRequest
    ) -> EditMetadataResponse:
        """
        Create a split event edit.

        Args:
            session: Database session
            user: User creating the split
            request: Split request with source node and new team details

        Returns:
            EditMetadataResponse with edit_id, status, and message

        Raises:
            ValueError: If validation fails (invalid UUIDs, missing team, inactive team)
        """
        # Validate source node exists
        try:
            node_id = UUID(request.source_node_id)
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid node_id format: {request.source_node_id}")

        # Eager-load eras relationship to avoid lazy loading in async context
        stmt = select(TeamNode).where(TeamNode.node_id == node_id).options(selectinload(TeamNode.eras))
        result = await session.execute(stmt)
        source_node = result.scalar_one_or_none()

        if not source_node:
            raise ValueError("Source team not found")

        # Check node is active in split year
        has_era = any(era.season_year == request.split_year for era in source_node.eras)
        if not has_era:
            raise ValueError(f"Team was not active in {request.split_year}")

        # Create edit record
        edit = Edit(
            user_id=user.user_id,
            edit_type=EditType.SPLIT,
            target_node_id=node_id,
            changes={
                'split_year': request.split_year,
                'new_teams': [
                    {'name': team.name, 'tier': team.tier}
                    for team in request.new_teams
                ]
            },
            reason=request.reason
        )

        # Auto-approve for trusted users and admins
        if user.role in [UserRole.TRUSTED_USER, UserRole.ADMIN]:
            edit.status = EditStatus.APPROVED
            edit.reviewed_by = user.user_id
            edit.reviewed_at = datetime.utcnow()

            # Apply split immediately
            await EditService._apply_split(session, request, user)

            user.approved_edits_count += 1
            message = "Split created successfully"
        else:
            edit.status = EditStatus.PENDING
            message = "Split submitted for moderation"

        session.add(edit)
        await session.commit()
        await session.refresh(edit)

        return EditMetadataResponse(
            edit_id=str(edit.edit_id),
            status=edit.status.value,
            message=message
        )

    @staticmethod
    async def _apply_split(
        session: AsyncSession,
        request: SplitEventRequest,
        user: User
    ):
        """Apply a split: close old node, create new nodes with links"""
        # Get source node
        try:
            node_id = UUID(request.source_node_id)
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid node_id format: {request.source_node_id}")

        source_node = await session.get(TeamNode, node_id)
        if not source_node:
            raise ValueError("Source team not found")

        # Close source node
        source_node.dissolution_year = request.split_year
        source_node.updated_at = datetime.utcnow()

        # Create new team nodes
        for new_team_info in request.new_teams:
            # Create new node
            new_node = TeamNode(
                founding_year=request.split_year
            )
            session.add(new_node)
            await session.flush()  # Get node_id

            # Create first era
            new_era = TeamEra(
                node_id=new_node.node_id,
                season_year=request.split_year,
                registered_name=new_team_info.name,
                tier_level=new_team_info.tier,
                source_origin=f"user_{user.user_id}",
                is_manual_override=True
            )
            session.add(new_era)

            # Create SPLIT lineage event
            lineage_event = LineageEvent(
                previous_node_id=node_id,
                next_node_id=new_node.node_id,
                event_year=request.split_year,
                event_type=EventType.SPLIT,
                notes=f"Split from source team into {new_team_info.name}"
            )
            session.add(lineage_event)

        await session.commit()
