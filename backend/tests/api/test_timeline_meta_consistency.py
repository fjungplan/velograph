import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_timeline_meta_consistency(test_client: AsyncClient):
    resp = await test_client.get("/api/v1/timeline")
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data and isinstance(data["nodes"], list)
    assert "links" in data and isinstance(data["links"], list)
    assert "meta" in data and isinstance(data["meta"], dict)
    meta = data["meta"]
    # snake_case and presence checks
    assert "year_range" in meta
    assert "node_count" in meta
    assert "link_count" in meta
    # counts consistent
    assert meta["node_count"] == len(data["nodes"]) 
    assert meta["link_count"] == len(data["links"]) 
