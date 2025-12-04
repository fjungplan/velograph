from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.db.database import get_db
from app.core.security import verify_token
from app.models.user import User, UserRole


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    This dependency extracts the JWT token from the Authorization header,
    verifies it, and returns the corresponding User object from the database.
    
    Raises:
        HTTPException: If token is invalid, expired, or user not found.
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id_str = payload.get("sub")
    
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = UUID(user_id_str)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    stmt = select(User).where(User.user_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account banned: {user.banned_reason or 'No reason provided'}"
        )
    
    return user


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin role for the current user.
    
    This dependency checks that the authenticated user has ADMIN role.
    Use this for endpoints that should only be accessible to administrators.
    
    Raises:
        HTTPException: If user does not have admin role.
    """
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_editor(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require editor permissions (not banned).
    
    This dependency checks that the authenticated user has permission to edit
    (NEW_USER, TRUSTED_USER, or ADMIN) and is not banned.
    Use this for endpoints that allow users to create or modify data.
    
    Raises:
        HTTPException: If user cannot edit or is banned.
    """
    if not current_user.can_edit():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Editor access required. You may be banned or lack permissions."
        )
    return current_user


async def require_trusted_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require trusted user or admin role.
    
    This dependency checks that the authenticated user is either a TRUSTED_USER
    or ADMIN. Use this for endpoints that should skip moderation or have
    additional privileges.
    
    Raises:
        HTTPException: If user is not trusted or admin.
    """
    if current_user.role not in [UserRole.TRUSTED_USER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Trusted user status required"
        )
    return current_user
