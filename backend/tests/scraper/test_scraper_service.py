"""Tests for ScraperService."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.scraper_service import ScraperService
from app.scraper.models import ScrapedTeamData
from app.models.team import TeamNode, TeamEra


@pytest.mark.asyncio
async def test_upsert_new_team(db_session: AsyncSession):
    """Test upserting a new team creates node and era."""
    service = ScraperService(db=db_session)
    
    data = ScrapedTeamData(
        source="procyclingstats",
        team_name="Test Team",
        uci_code="TST",
        tier="WT",
        sponsors=["Test Sponsor"]
    )
    
    era = await service.upsert_scraped_data(data)
    
    assert era.era_id is not None
    assert era.registered_name == "Test Team"
    assert era.uci_code == "TST"
    assert era.tier_level == 1  # WT = 1
    assert era.is_manual_override is False
    assert era.source_origin == "procyclingstats"


@pytest.mark.asyncio
async def test_upsert_with_proteam_tier(db_session: AsyncSession):
    """Test tier conversion for ProTeam."""
    service = ScraperService(db=db_session)
    
    data = ScrapedTeamData(
        source="procyclingstats",
        team_name="ProTeam Test",
        uci_code="PTT",
        tier="PT",
        sponsors=[]
    )
    
    era = await service.upsert_scraped_data(data)
    
    assert era.tier_level == 2  # PT = 2


@pytest.mark.asyncio
async def test_upsert_with_continental_tier(db_session: AsyncSession):
    """Test tier conversion for Continental team."""
    service = ScraperService(db=db_session)
    
    data = ScrapedTeamData(
        source="procyclingstats",
        team_name="Continental Test",
        uci_code="CTT",
        tier="CT",
        sponsors=[]
    )
    
    era = await service.upsert_scraped_data(data)
    
    assert era.tier_level == 3  # CT = 3


@pytest.mark.asyncio
async def test_upsert_without_team_name(db_session: AsyncSession):
    """Test that missing team_name raises error."""
    service = ScraperService(db=db_session)
    
    data = ScrapedTeamData(
        source="procyclingstats",
        team_name="",
        uci_code="TST",
        tier=None,
        sponsors=[]
    )
    
    with pytest.raises(ValueError, match="team_name is required"):
        await service.upsert_scraped_data(data)


@pytest.mark.asyncio
async def test_upsert_without_uci_code(db_session: AsyncSession):
    """Test upserting team without UCI code."""
    service = ScraperService(db=db_session)
    
    data = ScrapedTeamData(
        source="procyclingstats",
        team_name="No Code Team",
        uci_code=None,
        tier="CT",
        sponsors=[]
    )
    
    era = await service.upsert_scraped_data(data)
    
    assert era.registered_name == "No Code Team"
    assert era.uci_code is None


@pytest.mark.asyncio
async def test_upsert_without_tier(db_session: AsyncSession):
    """Test upserting team without tier information."""
    service = ScraperService(db=db_session)
    
    data = ScrapedTeamData(
        source="procyclingstats",
        team_name="No Tier Team",
        uci_code="NTT",
        tier=None,
        sponsors=[]
    )
    
    era = await service.upsert_scraped_data(data)
    
    assert era.tier_level is None


@pytest.mark.asyncio
async def test_handle_sponsors_placeholder(db_session: AsyncSession):
    """Test that handle_sponsors is a placeholder."""
    service = ScraperService(db=db_session)
    
    # Create a node and era
    node = TeamNode(founding_year=2024)
    db_session.add(node)
    await db_session.flush()
    
    era = TeamEra(
        node_id=node.node_id,
        season_year=2024,
        registered_name="Test Team",
        uci_code="TST"
    )
    db_session.add(era)
    await db_session.commit()
    
    sponsors = await service.handle_sponsors(era, ["Sponsor1", "Sponsor2"])
    
    # Should return empty list (placeholder implementation)
    assert sponsors == []
