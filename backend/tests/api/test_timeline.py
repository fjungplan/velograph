import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_timeline_default_params(test_client: AsyncClient):
    resp = await test_client.get("/api/v1/timeline")
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data and "links" in data and "meta" in data
    assert isinstance(data["meta"]["year_range"], list)


@pytest.mark.asyncio
async def test_timeline_year_filter(test_client: AsyncClient, sample_teams_in_db):
    resp = await test_client.get("/api/v1/timeline", params={"start_year": 2021, "end_year": 2022})
    assert resp.status_code == 200
    data = resp.json()
    # All eras should be within the filter
    for n in data["nodes"]:
        for e in n["eras"]:
            assert 2021 <= e["year"] <= 2022


@pytest.mark.asyncio
async def test_timeline_tier_filter(test_client: AsyncClient, sample_teams_in_db):
    resp = await test_client.get("/api/v1/timeline", params={"tier_filter": [1]})
    assert resp.status_code == 200
    data = resp.json()
    for n in data["nodes"]:
        for e in n["eras"]:
            assert e["tier"] in [1]


@pytest.mark.asyncio
async def test_timeline_empty_db(test_client: AsyncClient):
    # Using a fresh test client without sample data will still return a valid structure
    resp = await test_client.get("/api/v1/timeline", params={"start_year": 1990, "end_year": 1991})
    assert resp.status_code == 200
    data = resp.json()
    assert data["nodes"] == [] or isinstance(data["nodes"], list)
    assert isinstance(data["links"], list)
