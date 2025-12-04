import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone
from uuid import uuid4

from app.services.auth_service import AuthService
from app.models.user import User, UserRole
from app.core.security import create_access_token, create_refresh_token, verify_token, hash_token


class TestAuthService:
    """Test suite for AuthService"""
    
    @pytest.mark.asyncio
    async def test_verify_google_token_success(self):
        """Test successful Google token verification"""
        mock_token = "valid_google_token"
        expected_user_info = {
            'google_id': '123456789',
            'email': 'test@example.com',
            'display_name': 'Test User',
            'avatar_url': 'https://example.com/avatar.jpg'
        }
        
        with patch('app.services.auth_service.id_token.verify_oauth2_token') as mock_verify:
            mock_verify.return_value = {
                'iss': 'accounts.google.com',
                'sub': '123456789',
                'email': 'test@example.com',
                'name': 'Test User',
                'picture': 'https://example.com/avatar.jpg'
            }
            
            result = await AuthService.verify_google_token(mock_token)
            
            assert result == expected_user_info
            mock_verify.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_verify_google_token_invalid(self):
        """Test Google token verification with invalid token"""
        mock_token = "invalid_token"
        
        with patch('app.services.auth_service.id_token.verify_oauth2_token') as mock_verify:
            mock_verify.side_effect = ValueError('Invalid token')
            
            result = await AuthService.verify_google_token(mock_token)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_verify_google_token_wrong_issuer(self):
        """Test Google token verification with wrong issuer"""
        mock_token = "token_with_wrong_issuer"
        
        with patch('app.services.auth_service.id_token.verify_oauth2_token') as mock_verify:
            mock_verify.return_value = {
                'iss': 'malicious.com',
                'sub': '123456789',
                'email': 'test@example.com'
            }
            
            result = await AuthService.verify_google_token(mock_token)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_or_create_user_new_user(self, db_session):
        """Test creating a new user"""
        google_user_info = {
            'google_id': 'new_google_id',
            'email': 'newuser@example.com',
            'display_name': 'New User',
            'avatar_url': 'https://example.com/new_avatar.jpg'
        }
        
        user = await AuthService.get_or_create_user(db_session, google_user_info)
        
        assert user is not None
        assert user.google_id == google_user_info['google_id']
        assert user.email == google_user_info['email']
        assert user.display_name == google_user_info['display_name']
        assert user.avatar_url == google_user_info['avatar_url']
        assert user.role == UserRole.NEW_USER
        assert user.is_banned is False
    
    @pytest.mark.asyncio
    async def test_get_or_create_user_existing_user(self, db_session, test_user):
        """Test retrieving an existing user"""
        google_user_info = {
            'google_id': test_user.google_id,
            'email': test_user.email,
            'display_name': 'Updated Name',
            'avatar_url': 'https://example.com/updated_avatar.jpg'
        }
        
        original_last_login = test_user.last_login_at
        
        user = await AuthService.get_or_create_user(db_session, google_user_info)
        
        assert user.user_id == test_user.user_id
        assert user.google_id == test_user.google_id
        # Last login should be updated
        assert user.last_login_at != original_last_login
    
    @pytest.mark.asyncio
    async def test_create_tokens(self, db_session, test_user):
        """Test creating access and refresh tokens"""
        tokens = await AuthService.create_tokens(db_session, test_user)
        
        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        assert tokens.token_type == "bearer"
        
        # Verify access token payload
        access_payload = verify_token(tokens.access_token)
        assert access_payload is not None
        assert access_payload['type'] == 'access'
        assert access_payload['sub'] == str(test_user.user_id)
        assert access_payload['email'] == test_user.email
        
        # Verify refresh token payload
        refresh_payload = verify_token(tokens.refresh_token)
        assert refresh_payload is not None
        assert refresh_payload['type'] == 'refresh'
        assert refresh_payload['sub'] == str(test_user.user_id)


class TestSecurityFunctions:
    """Test suite for security utility functions"""
    
    def test_create_and_verify_access_token(self):
        """Test creating and verifying an access token"""
        user_data = {
            "sub": str(uuid4()),
            "email": "test@example.com",
            "role": "NEW_USER"
        }
        
        token = create_access_token(user_data)
        assert token is not None
        
        payload = verify_token(token)
        assert payload is not None
        assert payload['type'] == 'access'
        assert payload['sub'] == user_data['sub']
        assert payload['email'] == user_data['email']
        assert payload['role'] == user_data['role']
        assert 'exp' in payload
    
    def test_create_and_verify_refresh_token(self):
        """Test creating and verifying a refresh token"""
        user_data = {
            "sub": str(uuid4())
        }
        
        token = create_refresh_token(user_data)
        assert token is not None
        
        payload = verify_token(token)
        assert payload is not None
        assert payload['type'] == 'refresh'
        assert payload['sub'] == user_data['sub']
        assert 'exp' in payload
        assert 'jti' in payload  # Should have unique identifier
    
    def test_verify_invalid_token(self):
        """Test verifying an invalid token"""
        invalid_token = "not.a.valid.token"
        
        payload = verify_token(invalid_token)
        assert payload is None
    
    def test_hash_and_verify_token_hash(self):
        """Test hashing and verifying token hash"""
        token = "some_refresh_token_value"
        
        hashed = hash_token(token)
        assert hashed is not None
        assert hashed != token  # Should be hashed
        
        # Verify by re-hashing and comparing
        from app.core.security import verify_token_hash
        assert verify_token_hash(token, hashed) is True
        assert verify_token_hash("wrong_token", hashed) is False


# Fixtures for tests
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
    await db_session.flush()
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
    await db_session.flush()
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
    await db_session.flush()
    await db_session.refresh(user)
    return user
