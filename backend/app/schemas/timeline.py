from typing import List, Optional
from pydantic import BaseModel, Field


class SponsorComposition(BaseModel):
    brand: str
    color: str = Field(pattern=r"^#([A-Fa-f0-9]{6})$")
    prominence: int = Field(ge=0, le=100)


class TimelineEra(BaseModel):
    era_id: str
    year: int
    name: str
    tier: Optional[int] = None
    uci_code: Optional[str] = None
    sponsors: List[SponsorComposition] = []


class TimelineNode(BaseModel):
    id: str
    founding_year: int
    dissolution_year: Optional[int] = None
    eras: List[TimelineEra] = []


class TimelineLink(BaseModel):
    source: str
    target: str
    year: int
    type: str


class TimelineMeta(BaseModel):
    year_range: List[int]
    node_count: int
    link_count: int


class TimelineResponse(BaseModel):
    nodes: List[TimelineNode]
    links: List[TimelineLink]
    meta: TimelineMeta
