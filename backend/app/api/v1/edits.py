from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.dependencies import get_current_user, require_editor
from app.models.user import User
from app.schemas.edits import EditMetadataRequest, EditMetadataResponse, MergeEventRequest
from app.services.edit_service import EditService

router = APIRouter(prefix="/api/v1/edits", tags=["edits"])


@router.post("/metadata", response_model=EditMetadataResponse)
async def edit_metadata(
    request: EditMetadataRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """
    Edit team era metadata.
    
    This endpoint allows authenticated users to submit edits to team metadata.
    - NEW_USER: Edits go to moderation queue (PENDING status)
    - TRUSTED_USER/ADMIN: Edits are auto-approved and applied immediately
    """
    try:
        result = await EditService.create_metadata_edit(
            session,
            current_user,
            request
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/merge", response_model=EditMetadataResponse)
async def create_merge(
    request: MergeEventRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """
    Create a team merge event.
    
    This endpoint allows authenticated users to merge multiple teams into a new team.
    - NEW_USER: Merge goes to moderation queue (PENDING status)
    - TRUSTED_USER/ADMIN: Merge is auto-approved and applied immediately
    """
    try:
        result = await EditService.create_merge_edit(
            session,
            current_user,
            request
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
