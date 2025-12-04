from sqlalchemy import Column, String, Integer, Boolean, Text, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base, utc_now
from app.db.types import GUID
import enum
import uuid


class UserRole(str, enum.Enum):
    GUEST = "GUEST"
    NEW_USER = "NEW_USER"
    TRUSTED_USER = "TRUSTED_USER"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    google_id = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    display_name = Column(String(255))
    avatar_url = Column(String(500))
    # Use SQLAlchemy Enum with native_enum=False to store as string but return enum
    role = Column(Enum(UserRole, native_enum=False), default=UserRole.NEW_USER, nullable=False)
    approved_edits_count = Column(Integer, default=0)
    is_banned = Column(Boolean, default=False)
    banned_reason = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=utc_now)
    last_login_at = Column(TIMESTAMP, nullable=True)
    updated_at = Column(TIMESTAMP, default=utc_now, onupdate=utc_now)
    
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    def can_edit(self) -> bool:
        return self.role in [UserRole.NEW_USER, UserRole.TRUSTED_USER, UserRole.ADMIN] and not self.is_banned
    
    def needs_moderation(self) -> bool:
        return self.role == UserRole.NEW_USER
    
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    token_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, default=utc_now)
    
    user = relationship("User", back_populates="refresh_tokens")
