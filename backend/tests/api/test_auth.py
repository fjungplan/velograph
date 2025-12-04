import pytest
from unittest.mock import patch, AsyncMock
from fastapi import status
from uuid import uuid4

from app.models.user import User, UserRole
from app.core.security import create_access_token, create_refresh_token


class TestAuthEndpoints:
    """Test suite for authentication API endpoints"""
    
    @pytest.mark.asyncio
    async def test_google_auth_success_new_user(self, test_client, db_session):
        """Test successful Google authentication for a new user"""
        mock_google_user_info = {
            'google_id': 'new_google_123',
            'email': 'newuser@example.com',
            'display_name': 'New User',
            'avatar_url': 'https://example.com/avatar.jpg'
        }
        
        with patch('app.api.v1.auth.AuthService.verify_google_token') as mock_verify:
            mock_verify.return_value = mock_google_user_info
            
            response = await test_client.post(
                "/api/v1/auth/google",
                json={"id_token": "valid_google_token"}
            )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_google_auth_success_existing_user(self, test_client, db_session, test_user):
        """Test successful Google authentication for an existing user"""
        mock_google_user_info = {
            'google_id': test_user.google_id,
            'email': test_user.email,
            'display_name': test_user.display_name,
            'avatar_url': test_user.avatar_url
        }
        
        with patch('app.api.v1.auth.AuthService.verify_google_token') as mock_verify:
            mock_verify.return_value = mock_google_user_info
            
            response = await test_client.post(
                "/api/v1/auth/google",
                json={"id_token": "valid_google_token"}
            )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    @pytest.mark.asyncio
    async def test_google_auth_invalid_token(self, test_client):
        """Test Google authentication with invalid token"""
        with patch('app.api.v1.auth.AuthService.verify_google_token') as mock_verify:
            mock_verify.return_value = None
            
            response = await test_client.post(
                "/api/v1/auth/google",
                json={"id_token": "invalid_token"}
            )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid Google token" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_google_auth_banned_user(self, test_client, db_session, banned_user):
        """Test Google authentication with a banned user"""
        mock_google_user_info = {
            'google_id': banned_user.google_id,
            'email': banned_user.email,
            'display_name': banned_user.display_name,
            'avatar_url': banned_user.avatar_url
        }
        
        with patch('app.api.v1.auth.AuthService.verify_google_token') as mock_verify:
            mock_verify.return_value = mock_google_user_info
            
            response = await test_client.post(
                "/api/v1/auth/google",
                json={"id_token": "valid_token"}
            )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "banned" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, test_client, db_session, test_user):
        """Test successful token refresh"""
        # Create a valid refresh token
        refresh_token = create_refresh_token({"sub": str(test_user.user_id)})
        
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, test_client):
        """Test token refresh with invalid token"""
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_refresh_token_wrong_type(self, test_client, test_user):
        """Test token refresh with access token instead of refresh token"""
        # Create an access token (wrong type)
        access_token = create_access_token({
            "sub": str(test_user.user_id),
            "email": test_user.email,
            "role": test_user.role.value
        })
        
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_refresh_token_nonexistent_user(self, test_client):
        """Test token refresh with token for non-existent user"""
        fake_user_id = str(uuid4())
        refresh_token = create_refresh_token({"sub": fake_user_id})
        
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_refresh_token_banned_user(self, test_client, banned_user):
        """Test token refresh for a banned user"""
        refresh_token = create_refresh_token({"sub": str(banned_user.user_id)})
        
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, test_client, test_user):
        """Test getting current user info with valid token"""
        access_token = create_access_token({
            "sub": str(test_user.user_id),
            "email": test_user.email,
            "role": test_user.role.value
        })
        
        response = await test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["display_name"] == test_user.display_name
        assert data["role"] == test_user.role.value
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, test_client):
        """Test getting current user without token"""
        response = await test_client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, test_client):
        """Test getting current user with invalid token"""
        response = await test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_get_current_user_banned(self, test_client, banned_user):
        """Test getting current user info for banned user"""
        access_token = create_access_token({
            "sub": str(banned_user.user_id),
            "email": banned_user.email,
            "role": banned_user.role.value
        })
        
        response = await test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAuthDependencies:
    """Test suite for authentication dependencies"""
    
    @pytest.mark.asyncio
    async def test_require_admin_success(self, test_client, admin_user):
        """Test admin-only endpoint with admin user"""
        access_token = create_access_token({
            "sub": str(admin_user.user_id),
            "email": admin_user.email,
            "role": admin_user.role.value
        })
        
        # This would be tested on an actual admin endpoint
        # For now, just verify the token works
        response = await test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"] == "ADMIN"
    
    @pytest.mark.asyncio
    async def test_require_editor_success(self, test_client, test_user):
        """Test editor permission with regular user"""
        access_token = create_access_token({
            "sub": str(test_user.user_id),
            "email": test_user.email,
            "role": test_user.role.value
        })
        
        response = await test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert test_user.can_edit() is True


# Fixtures
@pytest.fixture
async def test_user(db_session):
    """Create a test user"""
    user = User(
        google_id='test_google_id_123',
        email='testuser@example.com',
        display_name='Test User',
        avatar_url='https://example.com/avatar.jpg',
        role=UserRole.NEW_USER
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(db_session):
    """Create an admin user"""
    user = User(
        google_id='admin_google_id_456',
        email='admin@example.com',
        display_name='Admin User',
        role=UserRole.ADMIN
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def banned_user(db_session):
    """Create a banned user"""
    user = User(
        google_id='banned_google_id_789',
        email='banned@example.com',
        display_name='Banned User',
        role=UserRole.NEW_USER,
        is_banned=True,
        banned_reason='Violation of terms of service'
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
