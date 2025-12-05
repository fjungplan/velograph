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


class MergeEventRequest(BaseModel):
    source_node_ids: list[str]  # Team IDs being merged
    merge_year: int
    new_team_name: str
    new_team_tier: int
    reason: str
    
    @field_validator('source_node_ids')
    @classmethod
    def validate_sources(cls, v):
        if len(v) < 2:
            raise ValueError('Merge requires at least 2 source teams')
        if len(v) > 5:
            raise ValueError('Cannot merge more than 5 teams at once')
        return v
    
    @field_validator('merge_year')
    @classmethod
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v < 1900 or v > current_year + 1:
            raise ValueError(f'Year must be between 1900 and {current_year + 1}')
        return v
    
    @field_validator('new_team_name')
    @classmethod
    def validate_team_name(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Team name must be at least 3 characters')
        if len(v) > 200:
            raise ValueError('Team name cannot exceed 200 characters')
        return v.strip()
    
    @field_validator('new_team_tier')
    @classmethod
    def validate_tier(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError('Tier must be 1, 2, or 3')
        return v
    
    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Reason must be at least 10 characters')
        return v.strip()


class NewTeamInfo(BaseModel):
    name: str
    tier: int
    
    @field_validator('tier')
    @classmethod
    def validate_tier(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError('Tier must be 1, 2, or 3')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Team name must be at least 3 characters')
        if len(v) > 200:
            raise ValueError('Team name cannot exceed 200 characters')
        return v.strip()


class SplitEventRequest(BaseModel):
    source_node_id: str  # Team being split
    split_year: int
    new_teams: list[NewTeamInfo]  # 2-5 new teams
    reason: str
    
    @field_validator('new_teams')
    @classmethod
    def validate_new_teams(cls, v):
        if len(v) < 2:
            raise ValueError('Split requires at least 2 resulting teams')
        if len(v) > 5:
            raise ValueError('Cannot split into more than 5 teams')
        return v
    
    @field_validator('split_year')
    @classmethod
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v < 1900 or v > current_year + 1:
            raise ValueError(f'Year must be between 1900 and {current_year + 1}')
        return v
    
    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Reason must be at least 10 characters')
        return v.strip()
