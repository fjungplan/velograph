"""Schemas for mobile-optimized team detail/history responses."""
from typing import Optional
from pydantic import BaseModel, Field


class TransitionInfo(BaseModel):
    """Represents a lineage transition (predecessor or successor)."""
    year: int = Field(..., description="Year of the transition event")
    name: Optional[str] = Field(None, description="Name of the related team")
    event_type: str = Field(..., description="Classified transition type (MERGED_INTO, ACQUISITION, REVIVAL, SPLIT)")


class TeamHistoryEra(BaseModel):
    """Single era in the team's chronological history."""
    year: int = Field(..., description="Season year")
    name: str = Field(..., description="Registered team name")
    tier: Optional[int] = Field(None, description="UCI tier level (1, 2, 3)")
    uci_code: Optional[str] = Field(None, description="3-letter UCI code")
    status: str = Field(..., description="Era status: active, historical, dissolved")
    predecessor: Optional[TransitionInfo] = Field(None, description="Incoming lineage transition")
    successor: Optional[TransitionInfo] = Field(None, description="Outgoing lineage transition")


class LineageSummary(BaseModel):
    """High-level lineage flags for quick UI decisions."""
    has_predecessors: bool = Field(..., description="True if team has any incoming lineage")
    has_successors: bool = Field(..., description="True if team has any outgoing lineage")
    spiritual_succession: bool = Field(..., description="True if any spiritual succession events exist")


class TeamHistoryResponse(BaseModel):
    """Mobile-optimized chronological history for a team node."""
    node_id: str = Field(..., description="UUID of the team node")
    founding_year: int = Field(..., description="Year the team was founded")
    dissolution_year: Optional[int] = Field(None, description="Year dissolved, if applicable")
    timeline: list[TeamHistoryEra] = Field(..., description="Chronological list of eras")
    lineage_summary: LineageSummary = Field(..., description="Lineage overview")
