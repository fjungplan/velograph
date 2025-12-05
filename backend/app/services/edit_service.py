from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Dict
from uuid import UUID

from app.models.edit import Edit, EditType, EditStatus
from app.models.team import TeamEra
from app.models.user import User, UserRole
from app.schemas.edits import EditMetadataRequest, EditMetadataResponse


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
