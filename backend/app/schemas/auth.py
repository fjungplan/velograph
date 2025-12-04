from pydantic import BaseModel, EmailStr
from typing import Optional


class GoogleTokenRequest(BaseModel):
    """Request model for Google OAuth authentication"""
    id_token: str


class TokenResponse(BaseModel):
    """Response model containing JWT tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Request model for refreshing access token"""
    refresh_token: str


class UserResponse(BaseModel):
    """Response model for user information"""
    user_id: str
    email: EmailStr
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    approved_edits_count: int
    
    model_config = {"from_attributes": True}
