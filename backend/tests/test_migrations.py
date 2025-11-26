"""
Tests for database migrations and TeamNode model.
"""
import pytest
import uuid
from datetime import datetime
from sqlalchemy import text, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.team import TeamNode
from app.db.database import engine


@pytest.mark.asyncio
async def test_team_node_table_exists():
    """Test that team_node table exists after migrations."""
    async with engine.connect() as conn:
        # Query the database to check if table exists
        result = await conn.execute(
            text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'team_node'
                )
            """)
        )
        exists = result.scalar()
        assert exists is True, "team_node table should exist"


@pytest.mark.asyncio
async def test_team_node_table_structure():
    """Test that team_node table has the correct structure."""
    async with engine.connect() as conn:
        # Check table columns
        result = await conn.execute(
            text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'team_node'
                ORDER BY ordinal_position
            """)
        )
        columns = {row[0]: {"type": row[1], "nullable": row[2]} for row in result}
        
        # Verify expected columns exist
        assert "node_id" in columns
        assert "founding_year" in columns
        assert "dissolution_year" in columns
        assert "created_at" in columns
        assert "updated_at" in columns
        
        # Verify nullability
        assert columns["node_id"]["nullable"] == "NO"
        assert columns["founding_year"]["nullable"] == "NO"
        assert columns["dissolution_year"]["nullable"] == "YES"
        assert columns["created_at"]["nullable"] == "NO"
        assert columns["updated_at"]["nullable"] == "NO"


@pytest.mark.asyncio
async def test_team_node_indexes_exist():
    """Test that the expected indexes exist on team_node table."""
    async with engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = 'team_node'
            """)
        )
        indexes = [row[0] for row in result]
        
        # Check for expected indexes
        assert "idx_team_node_founding" in indexes
        assert "idx_team_node_dissolution" in indexes


@pytest.mark.asyncio
async def test_create_team_node(client):
    """Test creating a TeamNode instance and saving to database."""
    from app.db.database import async_session_maker
    
    async with async_session_maker() as session:
        async with session.begin():
            # Create a new team node
            team = TeamNode(
                founding_year=2010,
                dissolution_year=None
            )
            
            session.add(team)
            await session.flush()
            
            # Verify it was saved
            assert team.node_id is not None
            assert isinstance(team.node_id, uuid.UUID)
            assert team.founding_year == 2010
            assert team.dissolution_year is None
            assert team.created_at is not None
            assert team.updated_at is not None
            assert isinstance(team.created_at, datetime)
            assert isinstance(team.updated_at, datetime)
            
            # Clean up
            await session.delete(team)


@pytest.mark.asyncio
async def test_team_node_timestamps_auto_populate(client):
    """Test that created_at and updated_at are automatically populated."""
    from app.db.database import async_session_maker
    
    async with async_session_maker() as session:
        async with session.begin():
            team = TeamNode(founding_year=1995)
            
            session.add(team)
            await session.flush()
            
            # After saving, timestamps should be populated
            assert team.created_at is not None
            assert team.updated_at is not None
            assert team.created_at <= team.updated_at
            
            # Clean up
            await session.delete(team)


@pytest.mark.asyncio
async def test_team_node_founding_year_validation(client):
    """Test that founding_year validation works (must be >= 1900)."""
    from sqlalchemy.exc import IntegrityError
    from app.db.database import async_session_maker
    
    # The model validation should catch this before database
    with pytest.raises(ValueError, match="founding_year must be >= 1900"):
        team = TeamNode(founding_year=1800)


@pytest.mark.asyncio
async def test_team_node_with_dissolution_year(client):
    """Test creating a team node with a dissolution year."""
    from app.db.database import async_session_maker
    
    async with async_session_maker() as session:
        async with session.begin():
            team = TeamNode(
                founding_year=2000,
                dissolution_year=2015
            )
            
            session.add(team)
            await session.flush()
            
            assert team.dissolution_year == 2015
            
            # Clean up
            await session.delete(team)


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
async def test_team_node_query(client):
    """Test querying TeamNode from database."""
    from app.db.database import async_session_maker
    
    async with async_session_maker() as session:
        async with session.begin():
            # Create test data
            team1 = TeamNode(founding_year=2010)
            team2 = TeamNode(founding_year=2015, dissolution_year=2020)
            
            session.add_all([team1, team2])
            await session.flush()
            
            # Query using select statement
            result = await session.execute(select(TeamNode))
            teams = result.scalars().all()
            assert len(teams) >= 2
            
            # Clean up
            await session.delete(team1)
            await session.delete(team2)
