from google.oauth2 import id_token
from google.auth.transport import requests
from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, hash_token
from app.models.user import User, RefreshToken
from app.schemas.auth import TokenResponse


class AuthService:
    @staticmethod
    async def verify_google_token(token: str) -> Optional[Dict]:
        """Verify Google ID token and extract user info"""
        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=10  # Allow 10 seconds clock skew
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer')
            
            return {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'display_name': idinfo.get('name'),
                'avatar_url': idinfo.get('picture')
            }
        except ValueError as e:
            print(f"Token verification failed: {e}")
            return None
    
    @staticmethod
    async def get_or_create_user(
        session: AsyncSession,
        google_user_info: Dict
    ) -> User:
        """Get existing user or create new one"""
        stmt = select(User).where(User.google_id == google_user_info['google_id'])
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            # Update last login
            user.last_login_at = datetime.now(timezone.utc).replace(tzinfo=None)
            user.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            # Create new user
            user = User(
                google_id=google_user_info['google_id'],
                email=google_user_info['email'],
                display_name=google_user_info['display_name'],
                avatar_url=google_user_info['avatar_url']
            )
            session.add(user)
        
        # Flush to DB to get user_id, but don't commit yet (let caller manage transaction)
        await session.flush()
        await session.refresh(user)
        return user
    
    @staticmethod
    async def create_tokens(
        session: AsyncSession,
        user: User
    ) -> TokenResponse:
        """Create access and refresh tokens for user"""
        role_value = getattr(user.role, 'value', user.role)
        access_token = create_access_token(
            data={"sub": str(user.user_id), "email": user.email, "role": role_value}
        )
        
        refresh_token = create_refresh_token(
            data={"sub": str(user.user_id)}
        )
        
        # Store refresh token in database
        token_hash = hash_token(refresh_token)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)).replace(tzinfo=None)
        
        db_refresh_token = RefreshToken(
            user_id=user.user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        session.add(db_refresh_token)
        # Flush to DB but don't commit yet (let caller manage transaction)
        await session.flush()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
