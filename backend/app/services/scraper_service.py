"""Service layer for scraper operations."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.team import TeamNode, TeamEra
from ..models.sponsor import SponsorMaster, SponsorBrand
from ..scraper.models import ScrapedTeamData


class ScraperService:
    """Service for integrating scraped data into the database."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def upsert_scraped_data(self, data: ScrapedTeamData) -> TeamEra:
        """
        Insert or update team era data from scraper, respecting manual overrides.
        
        Args:
            data: Scraped team data
        
        Returns:
            TeamEra instance (new or updated)
        
        Raises:
            ValueError: If team_name is missing
        
        Note:
            This is a simplified implementation that creates TeamNode/TeamEra
            without full lineage tracking. Complete implementation would need
            to handle node creation, era management, and lineage events.
        """
        if not data.team_name:
            raise ValueError("team_name is required")
        
        # For now, create a simple placeholder TeamNode and TeamEra
        # In a full implementation, this would need to:
        # 1. Search for existing TeamNode by registered_name across eras
        # 2. Handle multi-year team tracking
        # 3. Manage lineage events
        
        # Simplified: Create new node and era
        node = TeamNode(founding_year=2024)
        self.db.add(node)
        await self.db.flush()  # Get node_id
        
        # Convert tier string to tier_level integer
        tier_level = None
        if data.tier:
            tier_map = {"WT": 1, "PT": 2, "CT": 3}
            tier_level = tier_map.get(data.tier)
        
        era = TeamEra(
            node_id=node.node_id,
            season_year=2024,
            registered_name=data.team_name,
            uci_code=data.uci_code,
            tier_level=tier_level,
            source_origin=data.source,
            is_manual_override=False
        )
        self.db.add(era)
        
        # Commit changes
        await self.db.commit()
        await self.db.refresh(era)
        
        return era
    
    async def handle_sponsors(
        self,
        era: TeamEra,
        sponsor_names: list[str]
    ) -> list[SponsorBrand]:
        """
        Handle sponsor associations for a team era.
        
        This is a placeholder for future implementation that would:
        - Create sponsor entities if they don't exist
        - Link sponsors to team eras via TeamSponsorLink
        - Respect manual overrides
        
        Args:
            era: TeamEra instance
            sponsor_names: List of sponsor names from scraper
        
        Returns:
            List of SponsorBrand instances
        """
        # TODO: Implement sponsor handling in future iteration
        return []
