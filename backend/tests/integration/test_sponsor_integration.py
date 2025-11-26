"""Integration tests for sponsor functionality."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import TeamNode, TeamEra
from app.services.sponsor_service import SponsorService


@pytest.mark.asyncio
class TestSponsorIntegration:
    """Integration tests for complete sponsor scenarios."""
    
    async def test_soudal_quick_step_scenario(self, db_session: AsyncSession):
        """Test the full Soudal-Quick-Step team scenario.
        
        This recreates a realistic scenario:
        - Master sponsor "Soudal Group"
        - Brand "Soudal" with blue color
        - Brand "Quick-Step" with white color
        - Link both to an era with 60/40 split
        - Verify jersey composition
        """
        # Create team node and era
        node = TeamNode(founding_year=2003)
        db_session.add(node)
        await db_session.flush()
        
        era = TeamEra(
            node_id=node.node_id,
            season_year=2023,
            registered_name="Soudal Quick-Step",
            uci_code="SOQ",
            tier_level=1
        )
        db_session.add(era)
        await db_session.flush()
        
        # Create master sponsor
        soudal_group = await SponsorService.create_master(
            db_session,
            legal_name="Soudal Group",
            industry_sector="Construction Materials"
        )
        await db_session.commit()
        
        # Create two brands under the same master
        soudal_brand = await SponsorService.create_brand(
            db_session,
            master_id=soudal_group.master_id,
            brand_name="Soudal",
            default_hex_color="#0066CC"  # Blue
        )
        
        quick_step_brand = await SponsorService.create_brand(
            db_session,
            master_id=soudal_group.master_id,
            brand_name="Quick-Step",
            default_hex_color="#FFFFFF"  # White
        )
        await db_session.commit()
        
        # Link Soudal as primary sponsor (60%)
        soudal_link = await SponsorService.link_sponsor_to_era(
            db_session,
            era_id=era.era_id,
            brand_id=soudal_brand.brand_id,
            rank_order=1,
            prominence_percent=60
        )
        
        # Link Quick-Step as secondary sponsor (40%)
        quick_step_link = await SponsorService.link_sponsor_to_era(
            db_session,
            era_id=era.era_id,
            brand_id=quick_step_brand.brand_id,
            rank_order=2,
            prominence_percent=40
        )
        await db_session.commit()
        
        # Verify the links were created
        assert soudal_link.rank_order == 1
        assert soudal_link.prominence_percent == 60
        assert quick_step_link.rank_order == 2
        assert quick_step_link.prominence_percent == 40
        
        # Verify era validation
        validation = await SponsorService.validate_era_sponsors(
            db_session,
            era.era_id
        )
        assert validation['valid'] is True
        assert validation['total_percent'] == 100
        assert validation['sponsor_count'] == 2
        assert validation['remaining_percent'] == 0
        
        # Get jersey composition for visualization
        composition = await SponsorService.get_era_jersey_composition(
            db_session,
            era.era_id
        )
        
        assert len(composition) == 2
        
        # Verify primary sponsor (Soudal)
        assert composition[0]['brand_name'] == "Soudal"
        assert composition[0]['color'] == "#0066CC"
        assert composition[0]['prominence_percent'] == 60
        assert composition[0]['rank_order'] == 1
        
        # Verify secondary sponsor (Quick-Step)
        assert composition[1]['brand_name'] == "Quick-Step"
        assert composition[1]['color'] == "#FFFFFF"
        assert composition[1]['prominence_percent'] == 40
        assert composition[1]['rank_order'] == 2
        
        # Verify TeamEra properties
        await db_session.refresh(era, ["sponsor_links"])
        assert len(era.sponsor_links) == 2
        assert era.validate_sponsor_total() is True
        
        ordered_sponsors = era.sponsors_ordered
        assert ordered_sponsors[0].brand.brand_name == "Soudal"
        assert ordered_sponsors[1].brand.brand_name == "Quick-Step"
    
    async def test_multi_master_sponsor_scenario(self, db_session: AsyncSession):
        """Test a scenario with sponsors from different master companies."""
        # Create team
        node = TeamNode(founding_year=2010)
        db_session.add(node)
        await db_session.flush()
        
        era = TeamEra(
            node_id=node.node_id,
            season_year=2024,
            registered_name="Multi-Sponsor Team",
            uci_code="MST",
            tier_level=1
        )
        db_session.add(era)
        await db_session.flush()
        
        # Create three different master sponsors
        bike_company = await SponsorService.create_master(
            db_session,
            "BikeManufacturer Inc",
            "Bicycle Manufacturing"
        )
        
        beverage_company = await SponsorService.create_master(
            db_session,
            "Energy Drinks Ltd",
            "Beverages"
        )
        
        apparel_company = await SponsorService.create_master(
            db_session,
            "Sportswear Corp",
            "Sports Apparel"
        )
        await db_session.commit()
        
        # Create one brand for each
        bike_brand = await SponsorService.create_brand(
            db_session,
            bike_company.master_id,
            "SuperBike",
            "#FF0000"  # Red
        )
        
        energy_brand = await SponsorService.create_brand(
            db_session,
            beverage_company.master_id,
            "PowerDrink",
            "#FFFF00"  # Yellow
        )
        
        apparel_brand = await SponsorService.create_brand(
            db_session,
            apparel_company.master_id,
            "ProKit",
            "#0000FF"  # Blue
        )
        await db_session.commit()
        
        # Link all three with different prominences
        await SponsorService.link_sponsor_to_era(
            db_session, era.era_id, bike_brand.brand_id, 1, 50
        )
        await SponsorService.link_sponsor_to_era(
            db_session, era.era_id, energy_brand.brand_id, 2, 30
        )
        await SponsorService.link_sponsor_to_era(
            db_session, era.era_id, apparel_brand.brand_id, 3, 20
        )
        await db_session.commit()
        
        # Verify composition
        composition = await SponsorService.get_era_jersey_composition(
            db_session,
            era.era_id
        )
        
        assert len(composition) == 3
        assert composition[0]['brand_name'] == "SuperBike"
        assert composition[0]['prominence_percent'] == 50
        assert composition[1]['brand_name'] == "PowerDrink"
        assert composition[1]['prominence_percent'] == 30
        assert composition[2]['brand_name'] == "ProKit"
        assert composition[2]['prominence_percent'] == 20
        
        # Verify total is valid
        validation = await SponsorService.validate_era_sponsors(db_session, era.era_id)
        assert validation['valid'] is True
        assert validation['total_percent'] == 100
        assert validation['sponsor_count'] == 3
    
    async def test_partial_sponsorship_scenario(self, db_session: AsyncSession):
        """Test a scenario where sponsors don't fill 100% of the jersey."""
        # Create team
        node = TeamNode(founding_year=2015)
        db_session.add(node)
        await db_session.flush()
        
        era = TeamEra(
            node_id=node.node_id,
            season_year=2024,
            registered_name="Partial Team",
            tier_level=2
        )
        db_session.add(era)
        await db_session.flush()
        
        # Create sponsor
        master = await SponsorService.create_master(db_session, "Small Sponsor Co")
        brand = await SponsorService.create_brand(
            db_session,
            master.master_id,
            "SmallBrand",
            "#00FF00"
        )
        await db_session.commit()
        
        # Link with only 75% prominence (leaving 25% unsponsored)
        await SponsorService.link_sponsor_to_era(
            db_session, era.era_id, brand.brand_id, 1, 75
        )
        await db_session.commit()
        
        # Verify validation
        validation = await SponsorService.validate_era_sponsors(db_session, era.era_id)
        assert validation['valid'] is True  # Still valid, just not complete
        assert validation['total_percent'] == 75
        assert validation['remaining_percent'] == 25
        assert validation['sponsor_count'] == 1
        
        # Verify composition
        composition = await SponsorService.get_era_jersey_composition(db_session, era.era_id)
        assert len(composition) == 1
        assert composition[0]['prominence_percent'] == 75
    
    async def test_sponsor_evolution_across_eras(self, db_session: AsyncSession):
        """Test how sponsors change across different team eras."""
        # Create team node
        node = TeamNode(founding_year=2010)
        db_session.add(node)
        await db_session.flush()
        
        # Create three eras (2020, 2021, 2022)
        era_2020 = TeamEra(
            node_id=node.node_id,
            season_year=2020,
            registered_name="Team Alpha 2020"
        )
        era_2021 = TeamEra(
            node_id=node.node_id,
            season_year=2021,
            registered_name="Team Alpha 2021"
        )
        era_2022 = TeamEra(
            node_id=node.node_id,
            season_year=2022,
            registered_name="Team Beta 2022"  # Rebrand
        )
        db_session.add_all([era_2020, era_2021, era_2022])
        await db_session.flush()
        
        # Create sponsors
        sponsor_a_master = await SponsorService.create_master(db_session, "Sponsor A")
        sponsor_b_master = await SponsorService.create_master(db_session, "Sponsor B")
        sponsor_c_master = await SponsorService.create_master(db_session, "Sponsor C")
        
        brand_a = await SponsorService.create_brand(
            db_session, sponsor_a_master.master_id, "Brand A", "#AA0000"
        )
        brand_b = await SponsorService.create_brand(
            db_session, sponsor_b_master.master_id, "Brand B", "#00AA00"
        )
        brand_c = await SponsorService.create_brand(
            db_session, sponsor_c_master.master_id, "Brand C", "#0000AA"
        )
        await db_session.commit()
        
        # 2020: Brand A (100%)
        await SponsorService.link_sponsor_to_era(
            db_session, era_2020.era_id, brand_a.brand_id, 1, 100
        )
        
        # 2021: Brand A (70%) + Brand B (30%)
        await SponsorService.link_sponsor_to_era(
            db_session, era_2021.era_id, brand_a.brand_id, 1, 70
        )
        await SponsorService.link_sponsor_to_era(
            db_session, era_2021.era_id, brand_b.brand_id, 2, 30
        )
        
        # 2022: Brand B (60%) + Brand C (40%) - Brand A dropped
        await SponsorService.link_sponsor_to_era(
            db_session, era_2022.era_id, brand_b.brand_id, 1, 60
        )
        await SponsorService.link_sponsor_to_era(
            db_session, era_2022.era_id, brand_c.brand_id, 2, 40
        )
        await db_session.commit()
        
        # Verify 2020 composition
        comp_2020 = await SponsorService.get_era_jersey_composition(db_session, era_2020.era_id)
        assert len(comp_2020) == 1
        assert comp_2020[0]['brand_name'] == "Brand A"
        
        # Verify 2021 composition
        comp_2021 = await SponsorService.get_era_jersey_composition(db_session, era_2021.era_id)
        assert len(comp_2021) == 2
        assert comp_2021[0]['brand_name'] == "Brand A"
        assert comp_2021[1]['brand_name'] == "Brand B"
        
        # Verify 2022 composition (Brand A gone, Brand C added)
        comp_2022 = await SponsorService.get_era_jersey_composition(db_session, era_2022.era_id)
        assert len(comp_2022) == 2
        assert comp_2022[0]['brand_name'] == "Brand B"
        assert comp_2022[1]['brand_name'] == "Brand C"
        
        # Verify all eras are still valid
        for era in [era_2020, era_2021, era_2022]:
            validation = await SponsorService.validate_era_sponsors(db_session, era.era_id)
            assert validation['valid'] is True
            assert validation['total_percent'] == 100
