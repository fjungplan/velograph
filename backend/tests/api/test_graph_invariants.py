import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

from sqlalchemy.ext.asyncio import AsyncSession

async def test_graph_nodes_links_invariants(test_client: AsyncClient, complex_lineage_tree, isolated_session: AsyncSession):
    # Default range should include the events we created
    # Ensure eras exist so nodes appear in the graph
    from app.models.team import TeamEra
    for node in [complex_lineage_tree["A"], complex_lineage_tree["B"], complex_lineage_tree["C"], complex_lineage_tree["D"]]:
        e = TeamEra(node_id=node.node_id, season_year=2000, registered_name="Graph Test", tier_level=1)
        isolated_session.add(e)
    await isolated_session.commit()

    resp = await test_client.get("/api/v1/timeline")
    assert resp.status_code == 200
    data = resp.json()
    nodes = data.get("nodes", [])
    links = data.get("links", [])
    meta = data.get("meta", {})

    # Basic invariants
    assert isinstance(nodes, list) and isinstance(links, list)
    assert isinstance(meta, dict)
    assert meta.get("node_count") == len(nodes)
    assert meta.get("link_count") == len(links)

    # Unique node ids
    node_ids = [n.get("id") for n in nodes]
    assert len(node_ids) == len(set(node_ids))

    # No orphan links: source/target exist in nodes
    id_set = set(node_ids)
    for l in links:
        assert l.get("source") in id_set
        assert l.get("target") in id_set

async def test_graph_deterministic_ordering(test_client: AsyncClient):
    # Two calls with same params should yield identical payloads
    r1 = await test_client.get("/api/v1/timeline")
    r2 = await test_client.get("/api/v1/timeline")
    assert r1.json() == r2.json()

async def test_multi_year_filtering_consistency(test_client: AsyncClient):
    # Narrow range
    r_narrow = await test_client.get("/api/v1/timeline?start_year=2000&end_year=2005")
    # Wide range
    r_wide = await test_client.get("/api/v1/timeline?start_year=1990&end_year=2015")

    assert r_narrow.status_code == 200 and r_wide.status_code == 200
    d_n = r_narrow.json()
    d_w = r_wide.json()

    # Narrow range node/link sets are subsets of wide range
    n_ids_n = {n["id"] for n in d_n["nodes"]}
    n_ids_w = {n["id"] for n in d_w["nodes"]}
    assert n_ids_n.issubset(n_ids_w)

    l_pairs_n = {(l["source"], l["target"]) for l in d_n["links"]}
    l_pairs_w = {(l["source"], l["target"]) for l in d_w["links"]}
    assert l_pairs_n.issubset(l_pairs_w)
