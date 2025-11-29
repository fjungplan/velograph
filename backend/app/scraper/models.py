from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ScrapedTeamData(BaseModel):
    """Raw data scraped from a source"""

    source: str  # 'pcs', 'wikipedia', etc.
    team_name: str
    uci_code: Optional[str] = None
    founding_year: Optional[int] = None
    dissolution_year: Optional[int] = None
    current_tier: Optional[int] = None
    sponsors: List[str] = []


class ScraperResult(BaseModel):
    """Result from scraping operation"""

    success: bool
    team_identifier: str
    data: Optional[ScrapedTeamData] = None
    error: Optional[str] = None
    scraped_at: datetime
