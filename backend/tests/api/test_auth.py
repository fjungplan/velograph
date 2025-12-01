import pytest
from unittest.mock import patch
from httpx import AsyncClient

from app.models.user import User, UserRole, RefreshToken
from app.core.security import create_access_token, create_refresh_token, hash_token
from datetime import datetime, timedelta


class TestAuthEndpoints:
    """Test auth API endpoints"""
    
    @pytest.mark.asyncio
    async def test_google_auth_success(self, client: AsyncClient, db_session):
        """Test successful Google authentication"""
        mock_google_info = {
            'google_id': 'google_123',
            'email': 'newuser@example.com',
            'display_name': 'New User',
            'avatar_url': 'https://example.com/avatar.jpg'
        }
        
        with patch('app.services.auth_service.AuthService.verify_google_token', return_value=mock_google_info):
            response = await client.post(
                "/api/v1/auth/google",
                json={"id_token": "fake_google_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_google_auth_invalid_token(self, client: AsyncClient):
        """Test Google auth with invalid token"""
        with patch('app.services.auth_service.AuthService.verify_google_token', return_value=None):
            response = await client.post(
                "/api/v1/auth/google",
                json={"id_token": "invalid_token"}
            )
        
        assert response.status_code == 401
        assert "Invalid Google token" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_google_auth_banned_user(self, client: AsyncClient):
        """Test Google auth with banned user returns 403"""
        # Mock both verify and get_or_create to simulate banned user flow
        from app.models.user import User, UserRole
        
        # Create a banned user object (not persisted)
        banned_user = User(
            google_id='banned_user_123',
            email='banned@example.com',
            is_banned=True,
            banned_reason='Terms violation',
            role=UserRole.NEW_USER
        )
        
        mock_google_info = {
            'google_id': 'banned_user_123',
            'email': 'banned@example.com',
            'display_name': 'Banned User',
            'avatar_url': 'https://example.com/avatar.jpg'
        }
        
        with patch('app.services.auth_service.AuthService.verify_google_token', return_value=mock_google_info), \
             patch('app.services.auth_service.AuthService.get_or_create_user', return_value=banned_user):
            response = await client.post(
                "/api/v1/auth/google",
                json={"id_token": "fake_token"}
            )
        
        assert response.status_code == 403
        assert "banned" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient, db_session):
        """Test successful token refresh"""
        # Create user
        user = User(
            google_id='refresh_test_123',
            email='refresh@example.com',
            role=UserRole.NEW_USER
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Create refresh token
        refresh_token = create_refresh_token(data={"sub": str(user.user_id)})
        token_hash = hash_token(refresh_token)
        db_refresh = RefreshToken(
            user_id=user.user_id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db_session.add(db_refresh)
        await db_session.commit()
        
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test refresh with invalid token"""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_refresh_token_access_token_used(self, client: AsyncClient, db_session):
        """Test refresh endpoint rejects access tokens"""
        user = User(
            google_id='access_test_123',
            email='access@example.com',
            role=UserRole.NEW_USER
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Try to use access token instead of refresh token
        access_token = create_access_token(data={"sub": str(user.user_id), "email": user.email, "role": user.role.value})
        
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token}
        )
        
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_me_success(self, client: AsyncClient, db_session):
        """Test getting current user info"""
        # Create user
        user = User(
            google_id='me_test_123',
            email='me@example.com',
            display_name='Me Test',
            avatar_url='https://example.com/me.jpg',
            role=UserRole.TRUSTED_USER,
            approved_edits_count=10
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.user_id), "email": user.email, "role": user.role.value}
        )
        
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"
        assert data["display_name"] == "Me Test"
        assert data["avatar_url"] == "https://example.com/me.jpg"
        assert data["role"] == "TRUSTED_USER"
        assert data["approved_edits_count"] == 10
    
    @pytest.mark.asyncio
    async def test_get_me_no_token(self, client: AsyncClient):
        """Test /me endpoint without authentication"""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # HTTPBearer returns 403 when no credentials
    
    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, client: AsyncClient):
        """Test /me endpoint with invalid token"""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_me_banned_user(self, client: AsyncClient, db_session):
        """Test /me endpoint with banned user"""
        user = User(
            google_id='banned_me_123',
            email='bannedme@example.com',
            role=UserRole.NEW_USER,
            is_banned=True,
            banned_reason='Spam'
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        access_token = create_access_token(
            data={"sub": str(user.user_id), "email": user.email, "role": user.role.value}
        )
        
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 403
        assert "banned" in response.json()["detail"].lower()


class TestAuthDependencies:
    """Test auth dependency functions"""
    
    @pytest.mark.asyncio
    async def test_require_editor_allows_new_user(self, client: AsyncClient, db_session):
        """Test require_editor allows NEW_USER"""
        user = User(
            google_id='editor_new_123',
            email='editornew@example.com',
            role=UserRole.NEW_USER,
            is_banned=False
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # User can edit
        assert user.can_edit() is True
    
    @pytest.mark.asyncio
    async def test_require_editor_allows_trusted_user(self, client: AsyncClient, db_session):
        """Test require_editor allows TRUSTED_USER"""
        user = User(
            google_id='editor_trusted_123',
            email='editortrusted@example.com',
            role=UserRole.TRUSTED_USER,
            is_banned=False
        )
        db_session.add(user)
        await db_session.commit()
        
        assert user.can_edit() is True
    
    @pytest.mark.asyncio
    async def test_require_editor_allows_admin(self, client: AsyncClient, db_session):
        """Test require_editor allows ADMIN"""
        user = User(
            google_id='editor_admin_123',
            email='editoradmin@example.com',
            role=UserRole.ADMIN,
            is_banned=False
        )
        db_session.add(user)
        await db_session.commit()
        
        assert user.can_edit() is True
    
    @pytest.mark.asyncio
    async def test_require_editor_blocks_guest(self, client: AsyncClient, db_session):
        """Test require_editor blocks GUEST"""
        user = User(
            google_id='editor_guest_123',
            email='editorguest@example.com',
            role=UserRole.GUEST,
            is_banned=False
        )
        db_session.add(user)
        await db_session.commit()
        
        assert user.can_edit() is False
    
    @pytest.mark.asyncio
    async def test_require_editor_blocks_banned(self, client: AsyncClient, db_session):
        """Test require_editor blocks banned users"""
        user = User(
            google_id='editor_banned_123',
            email='editorbanned@example.com',
            role=UserRole.TRUSTED_USER,
            is_banned=True
        )
        db_session.add(user)
        await db_session.commit()
        
        assert user.can_edit() is False
    
    @pytest.mark.asyncio
    async def test_require_admin_allows_admin_only(self, client: AsyncClient, db_session):
        """Test require_admin only allows ADMIN"""
        admin = User(
            google_id='admin_123',
            email='admin@example.com',
            role=UserRole.ADMIN
        )
        regular = User(
            google_id='regular_123',
            email='regular@example.com',
            role=UserRole.TRUSTED_USER
        )
        
        assert admin.is_admin() is True
        assert regular.is_admin() is False
