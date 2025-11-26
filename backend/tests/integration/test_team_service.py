"""Integration tests for TeamService using real database interactions."""
import uuid
import pytest
from sqlalchemy import select

from app.models.team import TeamNode
from app.services.team_service import TeamService
from app.core.exceptions import NodeNotFoundException


@pytest.mark.asyncio
async def test_full_team_service_workflow(isolated_session):
    # Create a node
    async with isolated_session.begin():
        node = TeamNode(founding_year=2010)
        isolated_session.add(node)
        await isolated_session.flush()
        node_id = node.node_id

    # Create multiple eras
    await TeamService.create_era(isolated_session, node_id=node_id, year=2018, registered_name="Alpha 2018")
    await TeamService.create_era(isolated_session, node_id=node_id, year=2019, registered_name="Alpha 2019", tier_level=1)
    await TeamService.create_era(isolated_session, node_id=node_id, year=2020, registered_name="Alpha 2020", uci_code="ALP")

    # Fetch node with eras
    fetched = await TeamService.get_node_with_eras(isolated_session, node_id=node_id)
    assert len(fetched.eras) == 3
    years = {e.season_year for e in fetched.eras}
    assert {2018, 2019, 2020} <= years

    # Query by year
    eras_2019 = await TeamService.get_eras_by_year(isolated_session, 2019)
    assert any(e.registered_name == "Alpha 2019" for e in eras_2019)


@pytest.mark.asyncio
async def test_team_service_node_not_found(isolated_session):
    with pytest.raises(NodeNotFoundException):
        await TeamService.get_node_with_eras(isolated_session, node_id=uuid.uuid4())
