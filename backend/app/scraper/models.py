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
    tier: Optional[str] = None  # 'WT', 'PT', 'CT'
    sponsors: List[str] = []


class ScraperResult(BaseModel):
    """Result from scraping operation"""

    success: bool
    data: Optional[ScrapedTeamData] = None
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)
