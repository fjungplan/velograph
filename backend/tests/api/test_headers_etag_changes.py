import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.team import TeamEra

pytestmark = pytest.mark.asyncio

async def test_timeline_etag_changes_on_data_mutation(test_client: AsyncClient, isolated_session: AsyncSession, sample_team_node):
    r1 = await test_client.get("/api/v1/timeline")
    etag1 = r1.headers.get("etag")
    assert etag1 is not None

    # Mutate data: add a new era for the sample team
    new_era = TeamEra(node_id=sample_team_node.node_id, season_year=2099, registered_name="Future Team", tier_level=1)
    isolated_session.add(new_era)
    await isolated_session.commit()

    # Invalidate cache to reflect data mutation
    inv = await test_client.post("/api/v1/admin/cache/invalidate")
    assert inv.status_code in (200, 204)

    # Request again with widened year range to include the new era
    r2 = await test_client.get("/api/v1/timeline?end_year=2100")
    etag2 = r2.headers.get("etag")
    assert etag2 is not None
    assert etag2 != etag1

async def test_teams_list_etag_changes_on_pagination(test_client: AsyncClient):
    r1 = await test_client.get("/api/v1/teams?skip=0&limit=5")
    etag1 = r1.headers.get("etag")
    assert etag1 is not None

    r2 = await test_client.get("/api/v1/teams?skip=5&limit=5")
    etag2 = r2.headers.get("etag")
    assert etag2 is not None
    assert etag2 != etag1
