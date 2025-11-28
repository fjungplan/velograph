import pytest


@pytest.mark.asyncio
async def test_team_history_no_lazy_load(test_client):
    # This relies on fixtures creating baseline data in SQLite.
    # Call an arbitrary history endpoint; should not raise MissingGreenlet.
    # Using a zero UUID should 404; then we create basic data in a separate test.
    resp = await test_client.get("/api/v1/teams/00000000-0000-0000-0000-000000000000/history")
    assert resp.status_code in (404, 200)


@pytest.mark.asyncio
async def test_timeline_no_lazy_load(test_client):
    # Ensure timeline endpoint returns successfully without async lazy-load errors.
    resp = await test_client.get("/api/v1/timeline?start_year=2000&end_year=2030&include_dissolved=true")
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data and "links" in data


@pytest.mark.asyncio
async def test_team_eras_no_lazy_load(test_client):
    # Hitting eras endpoint should not trigger MissingGreenlet due to lazy-loads.
    resp = await test_client.get("/api/v1/teams/00000000-0000-0000-0000-000000000000/eras")
    assert resp.status_code in (404, 200)


@pytest.mark.asyncio
async def test_team_by_id_no_lazy_load(test_client):
    # Team by id should not trigger async lazy-load; zero UUID may 404.
    resp = await test_client.get("/api/v1/teams/00000000-0000-0000-0000-000000000000")
    assert resp.status_code in (404, 200)


@pytest.mark.asyncio
async def test_list_teams_no_lazy_load(test_client):
    # Listing teams with pagination/filters should not cause lazy-load errors.
    resp = await test_client.get("/api/v1/teams?skip=0&limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data and "total" in data


@pytest.mark.asyncio
async def test_timeline_sponsors_shape_no_lazy_load(test_client):
    # Timeline sponsors (if present) should be fully materialized without lazy loads.
    resp = await test_client.get("/api/v1/timeline?start_year=2000&end_year=2030&include_dissolved=true")
    assert resp.status_code == 200
    payload = resp.json()
    for node in payload.get("nodes", []):
        for era in node.get("eras", []):
            sponsors = era.get("sponsors", [])
            if sponsors:
                # Check expected keys without triggering lazy loads (JSON already serialized)
                assert all(
                    set(s.keys()) >= {"brand", "color", "prominence"} for s in sponsors
                )


@pytest.mark.asyncio
async def test_sponsor_service_composition_no_lazy_load(isolated_session, sample_team_era):
    # Create a simple brand and link it to the sample era, then fetch composition.
    from app.services.sponsor_service import SponsorService
    from app.models.sponsor import SponsorMaster, SponsorBrand
    master = await SponsorService.create_master(isolated_session, legal_name="Acme Corp")
    brand = await SponsorService.create_brand(
        isolated_session, master_id=master.master_id, brand_name="Acme", default_hex_color="#112233"
    )
    await SponsorService.link_sponsor_to_era(
        isolated_session,
        era_id=sample_team_era.era_id,
        brand_id=brand.brand_id,
        rank_order=1,
        prominence_percent=80,
    )
    composition = await SponsorService.get_era_jersey_composition(isolated_session, sample_team_era.era_id)
    assert composition and composition[0]["brand_name"] == "Acme"
    assert composition[0]["color"] == "#112233"
    assert composition[0]["prominence_percent"] == 80