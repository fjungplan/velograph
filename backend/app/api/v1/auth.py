from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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
    """Authenticate with Google ID token"""
    # Verify Google token
    google_user_info = await AuthService.verify_google_token(request.id_token)
    
    if not google_user_info:
        raise HTTPException(status_code=401, detail="Invalid Google token")
    
    # Get or create user
    user = await AuthService.get_or_create_user(session, google_user_info)
    
    if user.is_banned:
        raise HTTPException(status_code=403, detail=f"Account banned: {user.banned_reason}")
    
    # Create tokens
    tokens = await AuthService.create_tokens(session, user)
    
    # Commit once at the end to persist changes
    await session.commit()
    
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    # Verify refresh token
    payload = verify_token(request.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user_id = payload.get("sub")
    # Get user
    stmt = select(User).where(User.user_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_banned:
        raise HTTPException(status_code=403, detail=f"Account banned: {user.banned_reason}")
    
    # Create tokens with new refresh token
    tokens = await AuthService.create_tokens(session, user)
    
    # Commit once at the end to persist changes
    await session.commit()
    
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse(
        user_id=str(current_user.user_id),
        email=current_user.email,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url,
        role=current_user.role.value,
        approved_edits_count=current_user.approved_edits_count,
    )
