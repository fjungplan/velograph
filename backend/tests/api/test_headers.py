import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_timeline_etag_and_304(test_client: AsyncClient):
    resp = await test_client.get("/api/v1/timeline")
    assert resp.status_code == 200
    etag = resp.headers.get("etag")
    cache_control = resp.headers.get("cache-control")
    assert etag is not None and etag.startswith('W/"')
    assert cache_control is not None and "max-age=300" in cache_control

    resp2 = await test_client.get("/api/v1/timeline", headers={"If-None-Match": etag})
    assert resp2.status_code == 304

async def test_teams_list_etag_and_304(test_client: AsyncClient):
    resp = await test_client.get("/api/v1/teams")
    assert resp.status_code == 200
    etag = resp.headers.get("etag")
    cache_control = resp.headers.get("cache-control")
    assert etag is not None and etag.startswith('W/"')
    assert cache_control is not None and "max-age=300" in cache_control

    resp2 = await test_client.get("/api/v1/teams", headers={"If-None-Match": etag})
    assert resp2.status_code == 304

async def test_team_detail_and_eras_etag_304(test_client: AsyncClient, sample_team_node):
    # Detail
    node_id = str(sample_team_node.node_id)
    r1 = await test_client.get(f"/api/v1/teams/{node_id}")
    assert r1.status_code == 200
    etag1 = r1.headers.get("etag")
    assert etag1 is not None and etag1.startswith('W/"')
    r1c = await test_client.get(f"/api/v1/teams/{node_id}", headers={"If-None-Match": etag1})
    assert r1c.status_code == 304
    # Eras
    r2 = await test_client.get(f"/api/v1/teams/{node_id}/eras")
    assert r2.status_code == 200
    etag2 = r2.headers.get("etag")
    assert etag2 is not None and etag2.startswith('W/"')
    r2c = await test_client.get(f"/api/v1/teams/{node_id}/eras", headers={"If-None-Match": etag2})
    assert r2c.status_code == 304
