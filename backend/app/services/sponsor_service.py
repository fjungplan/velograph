"""Service layer for sponsor-related operations."""
import uuid
from typing import Optional, Dict, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.sponsor import SponsorMaster, SponsorBrand, TeamSponsorLink
from app.models.team import TeamEra
from app.core.exceptions import ValidationException, NodeNotFoundException
from app.services.timeline_service import TimelineService


class SponsorService:
    """Business logic for sponsor operations."""

    @staticmethod
    async def create_master(
        session: AsyncSession,
        legal_name: str,
        industry_sector: Optional[str] = None
    ) -> SponsorMaster:
        """Create a new sponsor master entity.
        
        Args:
            session: Database session
            legal_name: Legal name of the sponsor (must be unique)
            industry_sector: Optional industry classification
            
        Returns:
            Created SponsorMaster instance
            
        Raises:
            ValidationException: If legal_name is empty or already exists
        """
        if not legal_name or not legal_name.strip():
            raise ValidationException("legal_name cannot be empty")
        
        # Check for duplicate
        result = await session.execute(
            select(SponsorMaster).where(SponsorMaster.legal_name == legal_name)
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise ValidationException(f"Sponsor master with legal_name '{legal_name}' already exists")
        
        master = SponsorMaster(
            legal_name=legal_name.strip(),
            industry_sector=industry_sector.strip() if industry_sector else None
        )
        session.add(master)
        await session.flush()
        return master

    @staticmethod
    async def create_brand(
        session: AsyncSession,
        master_id: uuid.UUID,
        brand_name: str,
        default_hex_color: str
    ) -> SponsorBrand:
        """Create a new sponsor brand under a master sponsor.
        
        Args:
            session: Database session
            master_id: UUID of parent SponsorMaster
            brand_name: Name of the brand
            default_hex_color: Hex color code (e.g., #FF5733)
            
        Returns:
            Created SponsorBrand instance
            
        Raises:
            NodeNotFoundException: If master_id doesn't exist
            ValidationException: If brand_name is empty or hex color is invalid
        """
        # Verify master exists
        result = await session.execute(
            select(SponsorMaster).where(SponsorMaster.master_id == master_id)
        )
        master = result.scalar_one_or_none()
        if not master:
            raise NodeNotFoundException(f"SponsorMaster with id {master_id} not found")
        
        if not brand_name or not brand_name.strip():
            raise ValidationException("brand_name cannot be empty")
        
        # Check for duplicate brand under same master
        result = await session.execute(
            select(SponsorBrand).where(
                SponsorBrand.master_id == master_id,
                SponsorBrand.brand_name == brand_name.strip()
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise ValidationException(
                f"Brand '{brand_name}' already exists under master '{master.legal_name}'"
            )
        
        brand = SponsorBrand(
            master_id=master_id,
            brand_name=brand_name.strip(),
            default_hex_color=default_hex_color
        )
        session.add(brand)
        await session.flush()
        return brand

    @staticmethod
    async def link_sponsor_to_era(
        session: AsyncSession,
        era_id: uuid.UUID,
        brand_id: uuid.UUID,
        rank_order: int,
        prominence_percent: int
    ) -> TeamSponsorLink:
        """Link a sponsor brand to a team era.
        
        Args:
            session: Database session
            era_id: UUID of TeamEra
            brand_id: UUID of SponsorBrand
            rank_order: Ranking position (1 = primary sponsor)
            prominence_percent: Percentage of jersey prominence (1-100)
            
        Returns:
            Created TeamSponsorLink instance
            
        Raises:
            NodeNotFoundException: If era_id or brand_id doesn't exist
            ValidationException: If prominence would exceed 100% or rank is duplicate
        """
        # Verify era exists
        result = await session.execute(
            select(TeamEra).where(TeamEra.era_id == era_id)
        )
        era = result.scalar_one_or_none()
        if not era:
            raise NodeNotFoundException(f"TeamEra with id {era_id} not found")
        
        # Verify brand exists
        result = await session.execute(
            select(SponsorBrand).where(SponsorBrand.brand_id == brand_id)
        )
        brand = result.scalar_one_or_none()
        if not brand:
            raise NodeNotFoundException(f"SponsorBrand with id {brand_id} not found")
        
        # Check for duplicate era-brand link
        result = await session.execute(
            select(TeamSponsorLink).where(
                TeamSponsorLink.era_id == era_id,
                TeamSponsorLink.brand_id == brand_id
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise ValidationException(
                f"Brand is already linked to this era"
            )
        
        # Check for duplicate rank_order
        result = await session.execute(
            select(TeamSponsorLink).where(
                TeamSponsorLink.era_id == era_id,
                TeamSponsorLink.rank_order == rank_order
            )
        )
        existing_rank = result.scalar_one_or_none()
        if existing_rank:
            raise ValidationException(
                f"Rank order {rank_order} is already taken for this era"
            )
        
        # Check if adding this would exceed 100% prominence
        result = await session.execute(
            select(func.sum(TeamSponsorLink.prominence_percent))
            .where(TeamSponsorLink.era_id == era_id)
        )
        current_total = result.scalar() or 0
        
        if current_total + prominence_percent > 100:
            raise ValidationException(
                f"Adding {prominence_percent}% would exceed 100% total "
                f"(current total: {current_total}%)"
            )
        
        link = TeamSponsorLink(
            era_id=era_id,
            brand_id=brand_id,
            rank_order=rank_order,
            prominence_percent=prominence_percent
        )
        session.add(link)
        await session.flush()
        # Invalidate timeline cache after data change
        TimelineService.invalidate_cache()
        return link

    @staticmethod
    async def validate_era_sponsors(
        session: AsyncSession,
        era_id: uuid.UUID
    ) -> Dict[str, any]:
        """Validate that an era's sponsor prominence totals <= 100%.
        
        Args:
            session: Database session
            era_id: UUID of TeamEra to validate
            
        Returns:
            Dict with validation results:
                - valid: bool
                - total_percent: int
                - sponsor_count: int
                - remaining_percent: int
        """
        result = await session.execute(
            select(
                func.count(TeamSponsorLink.link_id).label('count'),
                func.sum(TeamSponsorLink.prominence_percent).label('total')
            )
            .where(TeamSponsorLink.era_id == era_id)
        )
        row = result.one()
        
        sponsor_count = row.count or 0
        total_percent = int(row.total) if row.total else 0
        
        return {
            'valid': total_percent <= 100,
            'total_percent': total_percent,
            'sponsor_count': sponsor_count,
            'remaining_percent': 100 - total_percent
        }

    @staticmethod
    async def get_era_jersey_composition(
        session: AsyncSession,
        era_id: uuid.UUID
    ) -> List[Dict[str, any]]:
        """Get the jersey color composition for an era, ordered by rank.
        
        Args:
            session: Database session
            era_id: UUID of TeamEra
            
        Returns:
            List of dicts with sponsor info, ordered by rank_order:
                - brand_name: str
                - color: str (hex color)
                - prominence_percent: int
                - rank_order: int
                
        Raises:
            NodeNotFoundException: If era_id doesn't exist
        """
        result = await session.execute(
            select(TeamEra).where(TeamEra.era_id == era_id)
        )
        era = result.scalar_one_or_none()
        if not era:
            raise NodeNotFoundException(f"TeamEra with id {era_id} not found")
        
        result = await session.execute(
            select(TeamSponsorLink, SponsorBrand)
            .join(SponsorBrand, TeamSponsorLink.brand_id == SponsorBrand.brand_id)
            .where(TeamSponsorLink.era_id == era_id)
            .order_by(TeamSponsorLink.rank_order)
            .options(selectinload(TeamSponsorLink.brand))
        )
        rows = result.all()
        
        composition = []
        for link, brand in rows:
            composition.append({
                'brand_name': brand.brand_name,
                'color': brand.default_hex_color,
                'prominence_percent': link.prominence_percent,
                'rank_order': link.rank_order
            })
        
        return composition
