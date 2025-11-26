"""
Tests for database migrations and TeamNode model.
"""
import pytest
import uuid
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import select
from app.models.team import TeamNode
from app.db.database import async_session_maker


@pytest.mark.asyncio
async def test_team_node_table_exists(isolated_engine):
    """Table should exist after migration (fresh engine)."""
    async with isolated_engine.connect() as conn:
        def _has_table(sync_conn):
            insp = sa.inspect(sync_conn)
            return insp.has_table("team_node")

        exists = await conn.run_sync(_has_table)
        assert exists is True


@pytest.mark.asyncio
async def test_team_node_table_structure(isolated_engine):
    """Column names and nullability should match expectations."""
    async with isolated_engine.connect() as conn:
        # Use SQLAlchemy's inspector for cross-database compatibility
        def _get_columns(sync_conn):
            insp = sa.inspect(sync_conn)
            return insp.get_columns("team_node")

        cols = await conn.run_sync(_get_columns)
        columns = {c["name"]: {"nullable": c.get("nullable", True)} for c in cols}

        for name in ["node_id", "founding_year", "dissolution_year", "created_at", "updated_at"]:
            assert name in columns

        # Inspector returns booleans for nullability across dialects
        assert columns["node_id"]["nullable"] is False
        assert columns["founding_year"]["nullable"] is False
        assert columns["dissolution_year"]["nullable"] is True
        assert columns["created_at"]["nullable"] is False
        assert columns["updated_at"]["nullable"] is False


@pytest.mark.asyncio
async def test_team_node_indexes_exist(isolated_engine):
    """Index names should be present (PostgreSQL migration run).

    Note: In this test suite we create tables via Base.metadata.create_all on
    SQLite for speed. That path doesn't create the Alembic-named indexes.
    Therefore, only enforce index name checks on PostgreSQL dialects where
    migrations are applied with explicit names.
    """
    async with isolated_engine.connect() as conn:
        def _get_index_names_and_dialect(sync_conn):
            insp = sa.inspect(sync_conn)
            return sync_conn.dialect.name, [idx["name"] for idx in insp.get_indexes("team_node")]

        dialect, names = await conn.run_sync(_get_index_names_and_dialect)
        if dialect != "postgresql":
            pytest.skip("Index name assertions are Postgres-specific; SQLite + create_all doesn't include them.")
        indexes = set(names)
        assert "idx_team_node_founding" in indexes
        assert "idx_team_node_dissolution" in indexes


@pytest.mark.asyncio
async def test_create_team_node(isolated_session):
    """Creating and flushing a TeamNode should populate fields."""
    async with isolated_session.begin():
        team = TeamNode(founding_year=2010)
        isolated_session.add(team)
        await isolated_session.flush()
        assert isinstance(team.node_id, uuid.UUID)
        assert team.founding_year == 2010
        assert team.dissolution_year is None
        assert isinstance(team.created_at, datetime)
        assert isinstance(team.updated_at, datetime)


@pytest.mark.asyncio
async def test_team_node_timestamps_auto_populate(isolated_session):
    """Timestamps should auto-fill on insert."""
    async with isolated_session.begin():
        team = TeamNode(founding_year=1995)
        isolated_session.add(team)
        await isolated_session.flush()
        assert team.created_at is not None
        assert team.updated_at is not None
        assert team.created_at <= team.updated_at


@pytest.mark.asyncio
async def test_team_node_founding_year_validation(client):
    """Test that founding_year validation works (must be >= 1900)."""
    from sqlalchemy.exc import IntegrityError
    from app.db.database import async_session_maker
    
    # The model validation should catch this before database
    with pytest.raises(ValueError, match="founding_year must be >= 1900"):
        team = TeamNode(founding_year=1800)


@pytest.mark.asyncio
async def test_team_node_with_dissolution_year(isolated_session):
    """Dissolution year should persist."""
    async with isolated_session.begin():
        team = TeamNode(founding_year=2000, dissolution_year=2015)
        isolated_session.add(team)
        await isolated_session.flush()
        assert team.dissolution_year == 2015


@pytest.mark.asyncio
async def test_team_node_repr():
    """Test the __repr__ method of TeamNode."""
    team = TeamNode(founding_year=2010, dissolution_year=2020)
    team.node_id = uuid.uuid4()
    
    repr_str = repr(team)
    assert "TeamNode" in repr_str
    assert "2010" in repr_str
    assert "2020" in repr_str
    assert str(team.node_id) in repr_str


@pytest.mark.asyncio
async def test_team_node_query(isolated_session):
    """Selecting TeamNode rows should return inserted items."""
    async with isolated_session.begin():
        team1 = TeamNode(founding_year=2010)
        team2 = TeamNode(founding_year=2015, dissolution_year=2020)
        isolated_session.add_all([team1, team2])
        await isolated_session.flush()
        result = await isolated_session.execute(select(TeamNode))
        teams = result.scalars().all()
        assert len(teams) >= 2
