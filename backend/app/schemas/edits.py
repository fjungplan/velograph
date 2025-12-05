from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class EditMetadataRequest(BaseModel):
    era_id: str
    registered_name: Optional[str] = None
    uci_code: Optional[str] = None
    tier_level: Optional[int] = None
    reason: str  # Why this edit is being made
    
    @field_validator('uci_code')
    @classmethod
    def validate_uci_code(cls, v):
        if v and (len(v) != 3 or not v.isupper()):
            raise ValueError('UCI code must be exactly 3 uppercase letters')
        return v
    
    @field_validator('tier_level')
    @classmethod
    def validate_tier(cls, v):
        if v and v not in [1, 2, 3]:
            raise ValueError('Tier must be 1, 2, or 3')
        return v
    
    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        if len(v) < 10:
            raise ValueError('Reason must be at least 10 characters')
        return v


class EditMetadataResponse(BaseModel):
    model_config = {"from_attributes": True}
    
    edit_id: str
    status: str  # 'PENDING' or 'APPROVED'
    message: str
