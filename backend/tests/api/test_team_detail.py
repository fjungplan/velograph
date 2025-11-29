import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.team import TeamNode, TeamEra
from app.models.lineage import LineageEvent
from app.models.enums import EventType


@pytest.mark.asyncio
async def test_team_history_basic(test_client, isolated_session: AsyncSession):
    # Setup: create node and eras
    node = TeamNode(founding_year=2010)
    isolated_session.add(node)
    await isolated_session.flush()
    await isolated_session.refresh(node)
    e2010 = TeamEra(node_id=node.node_id, season_year=2010, registered_name="Team Sky", tier_level=1, uci_code="SKY")
    e2020 = TeamEra(node_id=node.node_id, season_year=2020, registered_name="Ineos Grenadiers", tier_level=1, uci_code="IGD")
    isolated_session.add(e2010)
    isolated_session.add(e2020)
    await isolated_session.commit()

    resp = await test_client.get(f"/api/v1/teams/{node.node_id}/history")
    assert resp.status_code == 200
    assert resp.headers.get("Cache-Control") == "max-age=300"
    assert resp.headers.get("ETag")
    data = resp.json()
    assert data["node_id"] == str(node.node_id)
    assert len(data["timeline"]) == 2
    assert data["timeline"][0]["name"] == "Team Sky"
    assert data["timeline"][1]["name"] == "Ineos Grenadiers"

    # Conditional request with If-None-Match should return 304
    etag = resp.headers.get("ETag")
    resp2 = await test_client.get(
        f"/api/v1/teams/{node.node_id}/history",
        headers={"If-None-Match": etag},
    )
    assert resp2.status_code == 304
    assert resp2.headers.get("ETag") == etag
    assert resp2.headers.get("Cache-Control") == "max-age=300"


@pytest.mark.asyncio
async def test_team_history_not_found(test_client):
    resp = await test_client.get("/api/v1/teams/00000000-0000-0000-0000-000000000000/history")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_team_history_successor_predecessor(test_client, isolated_session: AsyncSession):
    # Setup nodes
    prev = TeamNode(founding_year=2000)
    nextn = TeamNode(founding_year=2021)
    curr = TeamNode(founding_year=2010)
    isolated_session.add_all([prev, nextn, curr])
    await isolated_session.flush()
    await isolated_session.refresh(prev)
    await isolated_session.refresh(nextn)
    await isolated_session.refresh(curr)
    # eras
    isolated_session.add(TeamEra(node_id=prev.node_id, season_year=2015, registered_name="OldTeam"))
    isolated_session.add(TeamEra(node_id=curr.node_id, season_year=2020, registered_name="CurrentTeam"))
    isolated_session.add(TeamEra(node_id=nextn.node_id, season_year=2021, registered_name="NewTeam"))
    await isolated_session.flush()
    # events
    await isolated_session.merge(LineageEvent(previous_node_id=prev.node_id, next_node_id=curr.node_id, event_year=2016, event_type=EventType.LEGAL_TRANSFER))
    await isolated_session.merge(LineageEvent(previous_node_id=curr.node_id, next_node_id=nextn.node_id, event_year=2021, event_type=EventType.MERGE))
    await isolated_session.commit()

    resp = await test_client.get(f"/api/v1/teams/{curr.node_id}/history")
    assert resp.status_code == 200
    data = resp.json()
    era = data["timeline"][0]
    assert era["predecessor"]["event_type"] == "ACQUISITION"
    last = data["timeline"][-1]
    assert last["successor"]["event_type"] == "MERGED_INTO"
