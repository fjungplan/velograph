import pytest
from httpx import AsyncClient
from app.models.team import TeamNode, TeamEra
from app.models.lineage import LineageEvent
from app.models.enums import EventType


@pytest.mark.asyncio
async def test_timeline_integration_complex(isolated_session, test_client: AsyncClient):
    # Create A (2010-2015), B (2015-2020), C (2020-present), D (2012-2018)
    A = TeamNode(founding_year=2010, dissolution_year=2015)
    B = TeamNode(founding_year=2015, dissolution_year=2020)
    C = TeamNode(founding_year=2020)
    D = TeamNode(founding_year=2012, dissolution_year=2018)
    isolated_session.add_all([A, B, C, D])
    await isolated_session.commit()
    await isolated_session.refresh(A); await isolated_session.refresh(B); await isolated_session.refresh(C); await isolated_session.refresh(D)

    eras = [
        TeamEra(node_id=A.node_id, season_year=2010, registered_name="Team A", tier_level=2),
        TeamEra(node_id=B.node_id, season_year=2016, registered_name="Team B", tier_level=1),
        TeamEra(node_id=C.node_id, season_year=2021, registered_name="Team C", tier_level=1),
        TeamEra(node_id=D.node_id, season_year=2013, registered_name="Team D", tier_level=2),
    ]
    isolated_session.add_all(eras)
    await isolated_session.commit()

    # A -> B (2015), B -> C (2020), Merge A + D -> E (simplify: A -> D in 2016 as SPLIT)
    ev_ab = LineageEvent(previous_node_id=A.node_id, next_node_id=B.node_id, event_year=2015, event_type=EventType.LEGAL_TRANSFER)
    ev_bc = LineageEvent(previous_node_id=B.node_id, next_node_id=C.node_id, event_year=2020, event_type=EventType.LEGAL_TRANSFER)
    ev_ad = LineageEvent(previous_node_id=A.node_id, next_node_id=D.node_id, event_year=2016, event_type=EventType.SPLIT)
    isolated_session.add_all([ev_ab, ev_bc, ev_ad])
    await isolated_session.commit()

    # Call endpoint with range
    resp = await test_client.get("/api/v1/timeline", params={"start_year": 2010, "end_year": 2021})
    assert resp.status_code == 200
    graph = resp.json()

    node_ids = {n["id"] for n in graph["nodes"]}
    for link in graph["links"]:
        assert link["source"] in node_ids
        assert link["target"] in node_ids
