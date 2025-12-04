from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.database import get_db
from app.schemas.auth import GoogleTokenRequest, TokenResponse, RefreshTokenRequest, UserResponse
from app.services.auth_service import AuthService
from app.core.security import verify_token
from app.models.user import User
from app.api.dependencies import get_current_user


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/google", response_model=TokenResponse)
async def google_auth(
    request: GoogleTokenRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Authenticate with Google ID token.
    
    This endpoint accepts a Google ID token (obtained from Google OAuth flow on frontend),
    verifies it, and either creates a new user or retrieves an existing one.
    Returns JWT access and refresh tokens for subsequent API calls.
    """
    # Verify Google token
    google_user_info = await AuthService.verify_google_token(request.id_token)
    
    if not google_user_info:
        raise HTTPException(status_code=401, detail="Invalid Google token")
    
    # Get or create user
    user = await AuthService.get_or_create_user(session, google_user_info)
    
    if user.is_banned:
        raise HTTPException(
            status_code=403, 
            detail=f"Account banned: {user.banned_reason or 'No reason provided'}"
        )
    
    # Create tokens
    tokens = await AuthService.create_tokens(session, user)
    
    # Commit the transaction
    await session.commit()
    
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    When the access token expires (after 15 minutes), use this endpoint
    to get a new access token without requiring the user to re-authenticate.
    """
    # Verify refresh token
    payload = verify_token(request.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user_id_str = payload.get("sub")
    
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    try:
        user_id = UUID(user_id_str)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=401, detail="Invalid user ID in token")
    
    # Get user
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if user.is_banned:
        raise HTTPException(
            status_code=403,
            detail=f"Account banned: {user.banned_reason or 'No reason provided'}"
        )
    
    # Create new tokens
    tokens = await AuthService.create_tokens(session, user)
    
    # Commit the transaction
    await session.commit()
    
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information.
    
    Returns the profile information of the currently authenticated user.
    Requires a valid access token in the Authorization header.
    """
    return UserResponse(
        user_id=str(current_user.user_id),
        email=current_user.email,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url,
        role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        approved_edits_count=current_user.approved_edits_count
    )
