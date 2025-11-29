import pytest
import pytest_asyncio
from app.services.dto import build_timeline_era_dto, build_team_summary_dto
from app.models.team import TeamNode, TeamEra
from app.models.sponsor import SponsorMaster, SponsorBrand, TeamSponsorLink
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.sponsor import TeamSponsorLink


@pytest.mark.asyncio
async def test_build_timeline_era_dto_shape(isolated_session):
    node = TeamNode(founding_year=2000)
    era = TeamEra(node=node, season_year=2024, registered_name="Alpha", tier_level=1)
    master = SponsorMaster(legal_name="Contoso LLC")
    brand = SponsorBrand(master=master, brand_name="Contoso", default_hex_color="#112233")
    link = TeamSponsorLink(era=era, brand=brand, prominence_percent=70, rank_order=1)
    isolated_session.add_all([node, era, master, brand, link])
    await isolated_session.commit()
    await isolated_session.refresh(era)
    # Re-fetch era with sponsors eagerly loaded to avoid async lazy-load
    loaded_era = (
        await isolated_session.execute(
            select(TeamEra)
            .options(
                selectinload(TeamEra.sponsor_links).selectinload(TeamSponsorLink.brand),
                selectinload(TeamEra.node),
            )
            .where(TeamEra.era_id == era.era_id)
        )
    ).scalar_one()

    dto = build_timeline_era_dto(loaded_era)
    assert set(dto.keys()) == {"eraId", "nodeId", "year", "name", "tier", "sponsors"}
    assert isinstance(dto["sponsors"], list)
    assert dto["tier"] == 1
    assert dto["year"] == 2024
    assert dto["name"] == "Alpha"
    assert len(dto["sponsors"]) == 1
    s0 = dto["sponsors"][0]
    assert set(s0.keys()) == {"brandId", "name", "color", "prominence", "rank"}
    assert s0["name"] == "Contoso"
    assert s0["color"] == "#112233"
    assert s0["prominence"] == 70
    assert s0["rank"] == 1


@pytest.mark.asyncio
async def test_build_team_summary_dto_shape(isolated_session):
    node = TeamNode(founding_year=1995)
    era1 = TeamEra(node=node, season_year=2023, registered_name="Bravo", tier_level=2)
    era2 = TeamEra(node=node, season_year=2024, registered_name="Bravo Renewed", tier_level=1)
    isolated_session.add_all([node, era1, era2])
    await isolated_session.commit()
    # Re-fetch node with eras eagerly loaded to avoid async lazy-load
    loaded_node = (
        await isolated_session.execute(
            select(TeamNode).options(selectinload(TeamNode.eras)).where(TeamNode.node_id == node.node_id)
        )
    ).scalar_one()

    dto = build_team_summary_dto(loaded_node)
    assert set(dto.keys()) == {"nodeId", "foundingYear", "currentName", "currentTier"}
    assert dto["foundingYear"] == 1995
    assert dto["currentName"] in {"Bravo", "Bravo Renewed"}
    assert dto["currentTier"] in {1, 2}
