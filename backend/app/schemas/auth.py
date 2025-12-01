from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


class GoogleTokenRequest(BaseModel):
    id_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str
    email: EmailStr
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    approved_edits_count: int
