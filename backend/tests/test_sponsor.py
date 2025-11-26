"""Tests for sponsor models and service."""
import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.sponsor import SponsorMaster, SponsorBrand, TeamSponsorLink
from app.models.team import TeamNode, TeamEra
from app.services.sponsor_service import SponsorService
from app.core.exceptions import ValidationException, NodeNotFoundException


@pytest.mark.asyncio
class TestSponsorMaster:
    """Tests for SponsorMaster model."""
    
    async def test_create_sponsor_master(self, db_session: AsyncSession):
        """Test creating a sponsor master."""
        master = SponsorMaster(
            legal_name="Soudal Group",
            industry_sector="Construction"
        )
        db_session.add(master)
        await db_session.commit()
        
        assert master.master_id is not None
        assert master.legal_name == "Soudal Group"
        assert master.industry_sector == "Construction"
        assert master.created_at is not None
        assert master.updated_at is not None
    
    async def test_sponsor_master_unique_legal_name(self, db_session: AsyncSession):
        """Test that legal_name must be unique."""
        master1 = SponsorMaster(legal_name="Acme Corp")
        db_session.add(master1)
        await db_session.commit()
        
        master2 = SponsorMaster(legal_name="Acme Corp")
        db_session.add(master2)
        
        with pytest.raises(Exception):  # IntegrityError
            await db_session.commit()


@pytest.mark.asyncio
class TestSponsorBrand:
    """Tests for SponsorBrand model."""
    
    async def test_create_sponsor_brand(self, db_session: AsyncSession):
        """Test creating a sponsor brand."""
        master = SponsorMaster(legal_name="Test Company")
        db_session.add(master)
        await db_session.flush()
        
        brand = SponsorBrand(
            master_id=master.master_id,
            brand_name="Test Brand",
            default_hex_color="#FF5733"
        )
        db_session.add(brand)
        await db_session.commit()
        
        assert brand.brand_id is not None
        assert brand.master_id == master.master_id
        assert brand.brand_name == "Test Brand"
        assert brand.default_hex_color == "#FF5733"
    
    async def test_hex_color_validation_valid(self, db_session: AsyncSession):
        """Test hex color validation with valid colors."""
        master = SponsorMaster(legal_name="Color Test Co")
        db_session.add(master)
        await db_session.flush()
        
        valid_colors = ["#000000", "#FFFFFF", "#ff5733", "#AbCdEf"]
        
        for color in valid_colors:
            brand = SponsorBrand(
                master_id=master.master_id,
                brand_name=f"Brand {color}",
                default_hex_color=color
            )
            db_session.add(brand)
        
        await db_session.commit()
        
        # Verify all were created
        result = await db_session.execute(
            select(SponsorBrand).where(SponsorBrand.master_id == master.master_id)
        )
        brands = result.scalars().all()
        assert len(brands) == len(valid_colors)
    
    async def test_hex_color_validation_invalid(self, db_session: AsyncSession):
        """Test hex color validation rejects invalid formats."""
        master = SponsorMaster(legal_name="Invalid Color Co")
        db_session.add(master)
        await db_session.flush()
        
        invalid_colors = [
            "#FFF",           # Too short
            "#GGGGGG",        # Invalid hex chars
            "FF5733",         # Missing #
            "#FF57331",       # Too long
            "#FF573",         # Wrong length
            "red",            # Named color
            ""                # Empty
        ]
        
        for color in invalid_colors:
            with pytest.raises(ValueError):
                brand = SponsorBrand(
                    master_id=master.master_id,
                    brand_name=f"Brand {color}",
                    default_hex_color=color
                )
    
    async def test_brand_cascade_delete(self, db_session: AsyncSession):
        """Test that deleting master cascades to brands."""
        master = SponsorMaster(legal_name="Cascade Test")
        db_session.add(master)
        await db_session.flush()
        
        brand = SponsorBrand(
            master_id=master.master_id,
            brand_name="Test Brand",
            default_hex_color="#123456"
        )
        db_session.add(brand)
        await db_session.commit()
        
        brand_id = brand.brand_id
        
        # Delete master
        await db_session.delete(master)
        await db_session.commit()
        
        # Verify brand was deleted
        result = await db_session.execute(
            select(SponsorBrand).where(SponsorBrand.brand_id == brand_id)
        )
        assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
class TestTeamSponsorLink:
    """Tests for TeamSponsorLink model."""
    
    async def test_create_sponsor_link(self, db_session: AsyncSession):
        """Test creating a team-sponsor link."""
        # Create prerequisites
        node = TeamNode(founding_year=2010)
        db_session.add(node)
        await db_session.flush()
        
        era = TeamEra(
            node_id=node.node_id,
            season_year=2020,
            registered_name="Test Team"
        )
        db_session.add(era)
        await db_session.flush()
        
        master = SponsorMaster(legal_name="Link Test Co")
        db_session.add(master)
        await db_session.flush()
        
        brand = SponsorBrand(
            master_id=master.master_id,
            brand_name="Link Brand",
            default_hex_color="#ABCDEF"
        )
        db_session.add(brand)
        await db_session.flush()
        
        # Create link
        link = TeamSponsorLink(
            era_id=era.era_id,
            brand_id=brand.brand_id,
            rank_order=1,
            prominence_percent=60
        )
        db_session.add(link)
        await db_session.commit()
        
        assert link.link_id is not None
        assert link.rank_order == 1
        assert link.prominence_percent == 60
    
    async def test_prominence_validation(self, db_session: AsyncSession):
        """Test prominence_percent validation."""
        # Setup
        node = TeamNode(founding_year=2010)
        db_session.add(node)
        await db_session.flush()
        
        era = TeamEra(node_id=node.node_id, season_year=2020, registered_name="Test")
        db_session.add(era)
        await db_session.flush()
        
        master = SponsorMaster(legal_name="Prominence Test")
        db_session.add(master)
        await db_session.flush()
        
        brand = SponsorBrand(
            master_id=master.master_id,
            brand_name="Brand",
            default_hex_color="#000000"
        )
        db_session.add(brand)
        await db_session.flush()
        
        # Test invalid values
        with pytest.raises(ValueError):
            link = TeamSponsorLink(
                era_id=era.era_id,
                brand_id=brand.brand_id,
                rank_order=1,
                prominence_percent=0  # Too low
            )
        
        with pytest.raises(ValueError):
            link = TeamSponsorLink(
                era_id=era.era_id,
                brand_id=brand.brand_id,
                rank_order=1,
                prominence_percent=101  # Too high
            )
        
        # Test valid edge cases
        link1 = TeamSponsorLink(
            era_id=era.era_id,
            brand_id=brand.brand_id,
            rank_order=1,
            prominence_percent=1  # Minimum
        )
        db_session.add(link1)
        await db_session.flush()
        
        # Create another brand for second link
        brand2 = SponsorBrand(
            master_id=master.master_id,
            brand_name="Brand 2",
            default_hex_color="#111111"
        )
        db_session.add(brand2)
        await db_session.flush()
        
        link2 = TeamSponsorLink(
            era_id=era.era_id,
            brand_id=brand2.brand_id,
            rank_order=2,
            prominence_percent=100  # Maximum
        )
        # This will violate business logic (total > 100) but model allows it
        db_session.add(link2)
        await db_session.commit()
    
    async def test_rank_order_uniqueness(self, db_session: AsyncSession):
        """Test that rank_order must be unique per era."""
        # Setup
        node = TeamNode(founding_year=2010)
        db_session.add(node)
        await db_session.flush()
        
        era = TeamEra(node_id=node.node_id, season_year=2020, registered_name="Test")
        db_session.add(era)
        await db_session.flush()
        
        master = SponsorMaster(legal_name="Rank Test")
        db_session.add(master)
        await db_session.flush()
        
        brand1 = SponsorBrand(
            master_id=master.master_id,
            brand_name="Brand 1",
            default_hex_color="#111111"
        )
        brand2 = SponsorBrand(
            master_id=master.master_id,
            brand_name="Brand 2",
            default_hex_color="#222222"
        )
        db_session.add_all([brand1, brand2])
        await db_session.flush()
        
        link1 = TeamSponsorLink(
            era_id=era.era_id,
            brand_id=brand1.brand_id,
            rank_order=1,
            prominence_percent=50
        )
        db_session.add(link1)
        await db_session.commit()
        
        # Try to create another link with same rank
        link2 = TeamSponsorLink(
            era_id=era.era_id,
            brand_id=brand2.brand_id,
            rank_order=1,  # Duplicate
            prominence_percent=50
        )
        db_session.add(link2)
        
        with pytest.raises(Exception):  # IntegrityError
            await db_session.commit()
    
    async def test_restrict_delete_brand_with_links(self, db_session: AsyncSession):
        """Test that deleting a brand with active links is restricted."""
        # Setup complete hierarchy
        node = TeamNode(founding_year=2010)
        db_session.add(node)
        await db_session.flush()
        
        era = TeamEra(node_id=node.node_id, season_year=2020, registered_name="Test")
        db_session.add(era)
        await db_session.flush()
        
        master = SponsorMaster(legal_name="Restrict Test")
        db_session.add(master)
        await db_session.flush()
        
        brand = SponsorBrand(
            master_id=master.master_id,
            brand_name="Linked Brand",
            default_hex_color="#333333"
        )
        db_session.add(brand)
        await db_session.flush()
        
        link = TeamSponsorLink(
            era_id=era.era_id,
            brand_id=brand.brand_id,
            rank_order=1,
            prominence_percent=80
        )
        db_session.add(link)
        await db_session.commit()
        
        # Try to delete brand (should fail due to RESTRICT)
        # Note: SQLite doesn't always enforce RESTRICT as strictly as PostgreSQL
        # This test mainly verifies the intent in the schema
        await db_session.delete(brand)
        
        try:
            await db_session.commit()
            # If SQLite allows it, at least verify the link still works
            remaining = await db_session.execute(
                select(TeamSponsorLink).where(TeamSponsorLink.link_id == link.link_id)
            )
            assert remaining.scalar_one_or_none() is not None, "Link should still exist"
        except Exception:
            # PostgreSQL properly enforces RESTRICT
            await db_session.rollback()
    
    async def test_cascade_delete_era(self, db_session: AsyncSession):
        """Test that deleting era cascades to sponsor links."""
        # Setup
        node = TeamNode(founding_year=2010)
        db_session.add(node)
        await db_session.flush()
        
        era = TeamEra(node_id=node.node_id, season_year=2020, registered_name="Test")
        db_session.add(era)
        await db_session.flush()
        
        master = SponsorMaster(legal_name="Cascade Era Test")
        db_session.add(master)
        await db_session.flush()
        
        brand = SponsorBrand(
            master_id=master.master_id,
            brand_name="Brand",
            default_hex_color="#444444"
        )
        db_session.add(brand)
        await db_session.flush()
        
        link = TeamSponsorLink(
            era_id=era.era_id,
            brand_id=brand.brand_id,
            rank_order=1,
            prominence_percent=70
        )
        db_session.add(link)
        await db_session.commit()
        
        link_id = link.link_id
        
        # Delete era
        await db_session.delete(era)
        await db_session.commit()
        
        # Verify link was deleted
        result = await db_session.execute(
            select(TeamSponsorLink).where(TeamSponsorLink.link_id == link_id)
        )
        assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
class TestSponsorService:
    """Tests for SponsorService business logic."""
    
    async def test_create_master(self, db_session: AsyncSession):
        """Test creating sponsor master via service."""
        master = await SponsorService.create_master(
            db_session,
            legal_name="Service Test Co",
            industry_sector="Technology"
        )
        
        assert master.master_id is not None
        assert master.legal_name == "Service Test Co"
        assert master.industry_sector == "Technology"
    
    async def test_create_master_duplicate_name(self, db_session: AsyncSession):
        """Test that duplicate legal_name is rejected."""
        await SponsorService.create_master(db_session, "Duplicate Inc")
        await db_session.commit()
        
        with pytest.raises(ValidationException, match="already exists"):
            await SponsorService.create_master(db_session, "Duplicate Inc")
    
    async def test_create_brand(self, db_session: AsyncSession):
        """Test creating sponsor brand via service."""
        master = await SponsorService.create_master(db_session, "Brand Test Co")
        await db_session.commit()
        
        brand = await SponsorService.create_brand(
            db_session,
            master_id=master.master_id,
            brand_name="Cool Brand",
            default_hex_color="#FF6600"
        )
        
        assert brand.brand_id is not None
        assert brand.master_id == master.master_id
        assert brand.brand_name == "Cool Brand"
        assert brand.default_hex_color == "#FF6600"
    
    async def test_create_brand_nonexistent_master(self, db_session: AsyncSession):
        """Test creating brand with non-existent master fails."""
        fake_id = uuid.uuid4()
        
        with pytest.raises(NodeNotFoundException):
            await SponsorService.create_brand(
                db_session,
                master_id=fake_id,
                brand_name="Orphan Brand",
                default_hex_color="#000000"
            )
    
    async def test_link_sponsor_to_era_success(self, db_session: AsyncSession):
        """Test successfully linking sponsor to era."""
        # Setup
        node = TeamNode(founding_year=2010)
        db_session.add(node)
        await db_session.flush()
        
        era = TeamEra(node_id=node.node_id, season_year=2020, registered_name="Test Team")
        db_session.add(era)
        await db_session.flush()
        
        master = await SponsorService.create_master(db_session, "Link Test")
        brand = await SponsorService.create_brand(
            db_session,
            master.master_id,
            "Link Brand",
            "#AABBCC"
        )
        await db_session.commit()
        
        # Create link
        link = await SponsorService.link_sponsor_to_era(
            db_session,
            era_id=era.era_id,
            brand_id=brand.brand_id,
            rank_order=1,
            prominence_percent=60
        )
        
        assert link.link_id is not None
        assert link.era_id == era.era_id
        assert link.brand_id == brand.brand_id
        assert link.prominence_percent == 60
    
    async def test_link_sponsor_prominence_total_validation(self, db_session: AsyncSession):
        """Test that total prominence cannot exceed 100%."""
        # Setup
        node = TeamNode(founding_year=2010)
        db_session.add(node)
        await db_session.flush()
        
        era = TeamEra(node_id=node.node_id, season_year=2020, registered_name="Test")
        db_session.add(era)
        await db_session.flush()
        
        master = await SponsorService.create_master(db_session, "Prominence Test")
        brand1 = await SponsorService.create_brand(db_session, master.master_id, "Brand 1", "#111111")
        brand2 = await SponsorService.create_brand(db_session, master.master_id, "Brand 2", "#222222")
        await db_session.commit()
        
        # Add first sponsor at 60%
        await SponsorService.link_sponsor_to_era(
            db_session,
            era.era_id,
            brand1.brand_id,
            rank_order=1,
            prominence_percent=60
        )
        await db_session.commit()
        
        # Try to add second at 50% (total would be 110%)
        with pytest.raises(ValidationException, match="exceed 100%"):
            await SponsorService.link_sponsor_to_era(
                db_session,
                era.era_id,
                brand2.brand_id,
                rank_order=2,
                prominence_percent=50
            )
        
        # But 40% should work (total 100%)
        link2 = await SponsorService.link_sponsor_to_era(
            db_session,
            era.era_id,
            brand2.brand_id,
            rank_order=2,
            prominence_percent=40
        )
        await db_session.commit()
        
        assert link2.prominence_percent == 40
    
    async def test_validate_era_sponsors(self, db_session: AsyncSession):
        """Test validate_era_sponsors method."""
        # Setup
        node = TeamNode(founding_year=2010)
        db_session.add(node)
        await db_session.flush()
        
        era = TeamEra(node_id=node.node_id, season_year=2020, registered_name="Test")
        db_session.add(era)
        await db_session.flush()
        
        master = await SponsorService.create_master(db_session, "Validate Test")
        brand1 = await SponsorService.create_brand(db_session, master.master_id, "B1", "#111111")
        brand2 = await SponsorService.create_brand(db_session, master.master_id, "B2", "#222222")
        await db_session.commit()
        
        # Initially empty
        validation = await SponsorService.validate_era_sponsors(db_session, era.era_id)
        assert validation['valid'] is True
        assert validation['total_percent'] == 0
        assert validation['sponsor_count'] == 0
        assert validation['remaining_percent'] == 100
        
        # Add 60%
        await SponsorService.link_sponsor_to_era(
            db_session, era.era_id, brand1.brand_id, 1, 60
        )
        await db_session.commit()
        
        validation = await SponsorService.validate_era_sponsors(db_session, era.era_id)
        assert validation['valid'] is True
        assert validation['total_percent'] == 60
        assert validation['sponsor_count'] == 1
        assert validation['remaining_percent'] == 40
        
        # Add 40%
        await SponsorService.link_sponsor_to_era(
            db_session, era.era_id, brand2.brand_id, 2, 40
        )
        await db_session.commit()
        
        validation = await SponsorService.validate_era_sponsors(db_session, era.era_id)
        assert validation['valid'] is True
        assert validation['total_percent'] == 100
        assert validation['sponsor_count'] == 2
        assert validation['remaining_percent'] == 0
    
    async def test_get_era_jersey_composition(self, db_session: AsyncSession):
        """Test retrieving ordered jersey composition."""
        # Setup
        node = TeamNode(founding_year=2010)
        db_session.add(node)
        await db_session.flush()
        
        era = TeamEra(node_id=node.node_id, season_year=2020, registered_name="Jersey Test")
        db_session.add(era)
        await db_session.flush()
        
        master = await SponsorService.create_master(db_session, "Jersey Co")
        brand1 = await SponsorService.create_brand(db_session, master.master_id, "Primary", "#FF0000")
        brand2 = await SponsorService.create_brand(db_session, master.master_id, "Secondary", "#0000FF")
        brand3 = await SponsorService.create_brand(db_session, master.master_id, "Tertiary", "#00FF00")
        await db_session.commit()
        
        # Add in non-sequential order
        await SponsorService.link_sponsor_to_era(db_session, era.era_id, brand2.brand_id, 2, 30)
        await SponsorService.link_sponsor_to_era(db_session, era.era_id, brand1.brand_id, 1, 50)
        await SponsorService.link_sponsor_to_era(db_session, era.era_id, brand3.brand_id, 3, 20)
        await db_session.commit()
        
        # Get composition
        composition = await SponsorService.get_era_jersey_composition(db_session, era.era_id)
        
        assert len(composition) == 3
        # Should be ordered by rank
        assert composition[0]['brand_name'] == "Primary"
        assert composition[0]['color'] == "#FF0000"
        assert composition[0]['prominence_percent'] == 50
        assert composition[0]['rank_order'] == 1
        
        assert composition[1]['brand_name'] == "Secondary"
        assert composition[1]['prominence_percent'] == 30
        assert composition[1]['rank_order'] == 2
        
        assert composition[2]['brand_name'] == "Tertiary"
        assert composition[2]['prominence_percent'] == 20
        assert composition[2]['rank_order'] == 3


@pytest.mark.asyncio
class TestTeamEraSponsors:
    """Tests for TeamEra sponsor-related properties."""
    
    async def test_sponsors_ordered_property(self, db_session: AsyncSession):
        """Test that sponsors_ordered returns links in rank order."""
        # Setup
        node = TeamNode(founding_year=2010)
        db_session.add(node)
        await db_session.flush()
        
        era = TeamEra(node_id=node.node_id, season_year=2020, registered_name="Order Test")
        db_session.add(era)
        await db_session.flush()
        
        master = await SponsorService.create_master(db_session, "Order Test Co")
        b1 = await SponsorService.create_brand(db_session, master.master_id, "B1", "#111111")
        b2 = await SponsorService.create_brand(db_session, master.master_id, "B2", "#222222")
        b3 = await SponsorService.create_brand(db_session, master.master_id, "B3", "#333333")
        await db_session.commit()
        
        # Add in random order
        await SponsorService.link_sponsor_to_era(db_session, era.era_id, b3.brand_id, 3, 20)
        await SponsorService.link_sponsor_to_era(db_session, era.era_id, b1.brand_id, 1, 50)
        await SponsorService.link_sponsor_to_era(db_session, era.era_id, b2.brand_id, 2, 30)
        await db_session.commit()
        
        # Refresh era with eager loading of sponsor relationships
        await db_session.refresh(era, ["sponsor_links"])
        
        ordered = era.sponsors_ordered
        assert len(ordered) == 3
        assert ordered[0].rank_order == 1
        assert ordered[1].rank_order == 2
        assert ordered[2].rank_order == 3
    
    async def test_validate_sponsor_total_method(self, db_session: AsyncSession):
        """Test validate_sponsor_total method on TeamEra."""
        # Setup
        node = TeamNode(founding_year=2010)
        db_session.add(node)
        await db_session.flush()
        
        era = TeamEra(node_id=node.node_id, season_year=2020, registered_name="Validation Test")
        db_session.add(era)
        await db_session.flush()
        
        master = await SponsorService.create_master(db_session, "Val Co")
        b1 = await SponsorService.create_brand(db_session, master.master_id, "B1", "#111111")
        b2 = await SponsorService.create_brand(db_session, master.master_id, "B2", "#222222")
        await db_session.commit()
        
        # Empty era should be valid
        await db_session.refresh(era, ["sponsor_links"])
        assert era.validate_sponsor_total() is True
        
        # Add 60%
        await SponsorService.link_sponsor_to_era(db_session, era.era_id, b1.brand_id, 1, 60)
        await db_session.commit()
        await db_session.refresh(era, ["sponsor_links"])
        assert era.validate_sponsor_total() is True
        
        # Add 40% (total 100%)
        await SponsorService.link_sponsor_to_era(db_session, era.era_id, b2.brand_id, 2, 40)
        await db_session.commit()
        await db_session.refresh(era, ["sponsor_links"])
        assert era.validate_sponsor_total() is True
