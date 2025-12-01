import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from sqlalchemy import select

from app.models.user import User, UserRole, RefreshToken
from app.services.auth_service import AuthService
from app.core.security import create_access_token, create_refresh_token, verify_token, hash_token
from app.schemas.auth import TokenResponse


class TestAuthService:
    """Test AuthService functionality"""
    
    @pytest.mark.asyncio
    async def test_verify_google_token_valid(self):
        """Test successful Google token verification"""
        mock_idinfo = {
            'iss': 'accounts.google.com',
            'sub': 'google_user_123',
            'email': 'test@example.com',
            'name': 'Test User',
            'picture': 'https://example.com/avatar.jpg'
        }
        
        with patch('app.services.auth_service.id_token.verify_oauth2_token', return_value=mock_idinfo):
            result = await AuthService.verify_google_token('fake_token')
            
            assert result is not None
            assert result['google_id'] == 'google_user_123'
            assert result['email'] == 'test@example.com'
            assert result['display_name'] == 'Test User'
            assert result['avatar_url'] == 'https://example.com/avatar.jpg'
    
    @pytest.mark.asyncio
    async def test_verify_google_token_invalid_issuer(self):
        """Test Google token with invalid issuer"""
        mock_idinfo = {
            'iss': 'malicious.com',
            'sub': 'google_user_123',
            'email': 'test@example.com'
        }
        
        with patch('app.services.auth_service.id_token.verify_oauth2_token', return_value=mock_idinfo):
            result = await AuthService.verify_google_token('fake_token')
            assert result is None
    
    @pytest.mark.asyncio
    async def test_verify_google_token_verification_fails(self):
        """Test Google token verification failure"""
        with patch('app.services.auth_service.id_token.verify_oauth2_token', side_effect=ValueError('Invalid token')):
            result = await AuthService.verify_google_token('fake_token')
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_or_create_user_new_user(self, db_session):
        """Test creating a new user"""
        google_user_info = {
            'google_id': 'new_user_123',
            'email': 'newuser@example.com',
            'display_name': 'New User',
            'avatar_url': 'https://example.com/new.jpg'
        }
        
        user = await AuthService.get_or_create_user(db_session, google_user_info)
        
        assert user.google_id == 'new_user_123'
        assert user.email == 'newuser@example.com'
        assert user.display_name == 'New User'
        assert user.avatar_url == 'https://example.com/new.jpg'
        assert user.role == UserRole.NEW_USER
        assert user.approved_edits_count == 0
        assert user.is_banned is False
    
    @pytest.mark.asyncio
    async def test_get_or_create_user_existing_user(self, db_session):
        """Test retrieving an existing user"""
        # Create user first
        user = User(
            google_id='existing_user_123',
            email='existing@example.com',
            display_name='Existing User',
            role=UserRole.TRUSTED_USER,
            approved_edits_count=5
        )
        db_session.add(user)
        await db_session.commit()
        
        # Retrieve the same user
        google_user_info = {
            'google_id': 'existing_user_123',
            'email': 'existing@example.com',
            'display_name': 'Existing User Updated',
            'avatar_url': 'https://example.com/updated.jpg'
        }
        
        retrieved_user = await AuthService.get_or_create_user(db_session, google_user_info)
        
        assert retrieved_user.user_id == user.user_id
        assert retrieved_user.role == UserRole.TRUSTED_USER  # Role should not change
        assert retrieved_user.approved_edits_count == 5  # Count should not change
        assert retrieved_user.last_login_at is not None
    
    @pytest.mark.asyncio
    async def test_create_tokens(self, db_session):
        """Test token creation"""
        user = User(
            google_id='token_test_123',
            email='tokentest@example.com',
            display_name='Token Test User',
            role=UserRole.NEW_USER
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        tokens = await AuthService.create_tokens(db_session, user)
        
        assert isinstance(tokens, TokenResponse)
        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        assert tokens.token_type == "bearer"
        
        # Verify access token
        access_payload = verify_token(tokens.access_token)
        assert access_payload is not None
        assert access_payload['type'] == 'access'
        assert access_payload['email'] == user.email
        assert access_payload['role'] == UserRole.NEW_USER.value
        
        # Verify refresh token
        refresh_payload = verify_token(tokens.refresh_token)
        assert refresh_payload is not None
        assert refresh_payload['type'] == 'refresh'
        
        # Verify refresh token stored in database
        stmt = select(RefreshToken).where(RefreshToken.user_id == user.user_id)
        result = await db_session.execute(stmt)
        db_refresh_token = result.scalar_one_or_none()
        assert db_refresh_token is not None


class TestJWTSecurity:
    """Test JWT security utilities"""
    
    def test_create_and_verify_access_token(self):
        """Test creating and verifying access token"""
        data = {"sub": "user_123", "email": "test@example.com", "role": "NEW_USER"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload is not None
        assert payload['sub'] == "user_123"
        assert payload['email'] == "test@example.com"
        assert payload['role'] == "NEW_USER"
        assert payload['type'] == "access"
    
    def test_create_and_verify_refresh_token(self):
        """Test creating and verifying refresh token"""
        data = {"sub": "user_123"}
        token = create_refresh_token(data)
        
        payload = verify_token(token)
        assert payload is not None
        assert payload['sub'] == "user_123"
        assert payload['type'] == "refresh"
    
    def test_verify_invalid_token(self):
        """Test verifying invalid token"""
        payload = verify_token("invalid_token")
        assert payload is None
    
    def test_verify_expired_token(self):
        """Test verifying expired token"""
        data = {"sub": "user_123"}
        expires_delta = timedelta(seconds=-1)  # Expired
        token = create_access_token(data, expires_delta)
        
        payload = verify_token(token)
        assert payload is None
    
    def test_hash_and_verify_token(self):
        """Test hashing and verifying token"""
        token = "some_token_string"
        hashed = hash_token(token)
        
        assert hashed != token
        from app.core.security import verify_token_hash
        assert verify_token_hash(token, hashed) is True
        assert verify_token_hash("wrong_token", hashed) is False


class TestUserModel:
    """Test User model methods"""
    
    def test_can_edit_new_user(self):
        """Test NEW_USER can edit"""
        user = User(
            google_id="test_123",
            email="test@example.com",
            role=UserRole.NEW_USER,
            is_banned=False
        )
        assert user.can_edit() is True
    
    def test_can_edit_trusted_user(self):
        """Test TRUSTED_USER can edit"""
        user = User(
            google_id="test_123",
            email="test@example.com",
            role=UserRole.TRUSTED_USER,
            is_banned=False
        )
        assert user.can_edit() is True
    
    def test_can_edit_admin(self):
        """Test ADMIN can edit"""
        user = User(
            google_id="test_123",
            email="test@example.com",
            role=UserRole.ADMIN,
            is_banned=False
        )
        assert user.can_edit() is True
    
    def test_cannot_edit_guest(self):
        """Test GUEST cannot edit"""
        user = User(
            google_id="test_123",
            email="test@example.com",
            role=UserRole.GUEST,
            is_banned=False
        )
        assert user.can_edit() is False
    
    def test_cannot_edit_banned_user(self):
        """Test banned user cannot edit"""
        user = User(
            google_id="test_123",
            email="test@example.com",
            role=UserRole.TRUSTED_USER,
            is_banned=True
        )
        assert user.can_edit() is False
    
    def test_needs_moderation_new_user(self):
        """Test NEW_USER needs moderation"""
        user = User(
            google_id="test_123",
            email="test@example.com",
            role=UserRole.NEW_USER
        )
        assert user.needs_moderation() is True
    
    def test_no_moderation_trusted_user(self):
        """Test TRUSTED_USER doesn't need moderation"""
        user = User(
            google_id="test_123",
            email="test@example.com",
            role=UserRole.TRUSTED_USER
        )
        assert user.needs_moderation() is False
    
    def test_is_admin(self):
        """Test admin check"""
        admin_user = User(
            google_id="admin_123",
            email="admin@example.com",
            role=UserRole.ADMIN
        )
        regular_user = User(
            google_id="user_123",
            email="user@example.com",
            role=UserRole.NEW_USER
        )
        
        assert admin_user.is_admin() is True
        assert regular_user.is_admin() is False
