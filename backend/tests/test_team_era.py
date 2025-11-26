"""Tests for TeamEra model and TeamService logic."""
import uuid
import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from app.models.team import TeamNode, TeamEra
from app.services.team_service import TeamService
from app.core.exceptions import DuplicateEraException, ValidationException, NodeNotFoundException


@pytest.mark.asyncio
async def test_team_era_table_exists(isolated_engine):
    async with isolated_engine.connect() as conn:
        result = await conn.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='team_era')")
        )
        assert result.scalar() is True


@pytest.mark.asyncio
async def test_create_team_era_valid(isolated_session):
    async with isolated_session.begin():
        node = TeamNode(founding_year=2005)
        isolated_session.add(node)
        await isolated_session.flush()
        era = TeamEra(
            node_id=node.node_id,
            season_year=2020,
            registered_name="Example Cycling Team",
            uci_code="ECT",
            tier_level=1,
        )
        isolated_session.add(era)
        await isolated_session.flush()
        assert isinstance(era.era_id, uuid.UUID)
        assert era.is_manual_override is False
        assert era.display_name == "Example Cycling Team (ECT)"


@pytest.mark.asyncio
async def test_team_era_duplicate_constraint(isolated_session):
    async with isolated_session.begin():
        node = TeamNode(founding_year=2010)
        isolated_session.add(node)
        await isolated_session.flush()
        era1 = TeamEra(
            node_id=node.node_id,
            season_year=2021,
            registered_name="Dup Team",
        )
        isolated_session.add(era1)
        await isolated_session.flush()
        era2 = TeamEra(
            node_id=node.node_id,
            season_year=2021,
            registered_name="Dup Team Again",
        )
        isolated_session.add(era2)
        with pytest.raises(IntegrityError):
            await isolated_session.flush()


@pytest.mark.asyncio
async def test_team_service_create_era_and_duplicate(isolated_session):
    # Create node first
    async with isolated_session.begin():
        node = TeamNode(founding_year=2012)
        isolated_session.add(node)
        await isolated_session.flush()
        node_id = node.node_id
    # Create era via service
    era = await TeamService.create_era(
        isolated_session,
        node_id=node_id,
        year=2022,
        registered_name="Service Era",
    )
    assert era.season_year == 2022
    # Duplicate attempt
    with pytest.raises(DuplicateEraException):
        await TeamService.create_era(
            isolated_session,
            node_id=node_id,
            year=2022,
            registered_name="Service Era Again",
        )


@pytest.mark.asyncio
async def test_team_service_validation_errors(isolated_session):
    # Missing node
    with pytest.raises(NodeNotFoundException):
        await TeamService.create_era(
            isolated_session,
            node_id=uuid.uuid4(),
            year=2020,
            registered_name="No Node",
        )
    # Invalid tier level
    async with isolated_session.begin():
        node = TeamNode(founding_year=2010)
        isolated_session.add(node)
        await isolated_session.flush()
    with pytest.raises(ValidationException):
        await TeamService.create_era(
            isolated_session,
            node_id=node.node_id,
            year=2020,
            registered_name="Bad Tier",
            tier_level=4,
        )
    # Invalid UCI code
    with pytest.raises(ValidationException):
        await TeamService.create_era(
            isolated_session,
            node_id=node.node_id,
            year=2021,
            registered_name="Bad UCI",
            uci_code="AB",
        )


@pytest.mark.asyncio
async def test_get_eras_by_year(isolated_session):
    async with isolated_session.begin():
        node1 = TeamNode(founding_year=2000)
        node2 = TeamNode(founding_year=2005)
        isolated_session.add_all([node1, node2])
        await isolated_session.flush()
        isolated_session.add_all([
            TeamEra(node_id=node1.node_id, season_year=2024, registered_name="Alpha"),
            TeamEra(node_id=node2.node_id, season_year=2024, registered_name="Beta"),
        ])
        await isolated_session.flush()
    eras = await TeamService.get_eras_by_year(isolated_session, 2024)
    assert len(eras) >= 2
    names = {e.registered_name for e in eras}
    assert "Alpha" in names and "Beta" in names


@pytest.mark.asyncio
async def test_cascade_delete_node_deletes_eras(isolated_session):
    async with isolated_session.begin():
        node = TeamNode(founding_year=2015)
        isolated_session.add(node)
        await isolated_session.flush()
        era = TeamEra(node_id=node.node_id, season_year=2023, registered_name="To Delete")
        isolated_session.add(era)
        await isolated_session.flush()
        # Delete node
        await isolated_session.delete(node)
        await isolated_session.flush()
        # Era should be gone
        result = await isolated_session.execute(select(TeamEra).where(TeamEra.era_id == era.era_id))
        assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_team_era_validations(isolated_session):
    async with isolated_session.begin():
        node = TeamNode(founding_year=1999)
        isolated_session.add(node)
        await isolated_session.flush()
    # Empty registered_name
    with pytest.raises(ValueError):
        TeamEra(node_id=node.node_id, season_year=2020, registered_name="   ")
    # Bad UCI code length
    with pytest.raises(ValueError):
        TeamEra(node_id=node.node_id, season_year=2020, registered_name="X", uci_code="AB")
    # Bad UCI lowercase
    with pytest.raises(ValueError):
        TeamEra(node_id=node.node_id, season_year=2020, registered_name="X", uci_code="abc")
    # Bad tier level
    with pytest.raises(ValueError):
        TeamEra(node_id=node.node_id, season_year=2020, registered_name="X", tier_level=5)
