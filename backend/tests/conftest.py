import pytest
import pytest_asyncio
from httpx import AsyncClient
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.db.base import Base
from app.core.config import settings
from main import app
from app.db.database import get_db
from app.api.health import get_checker
from app.models.team import TeamNode, TeamEra
from app.models.lineage import LineageEvent
from app.models.enums import EventType
from app.models.user import User, UserRole
from app.core.security import create_access_token
import uuid
import app.db.database as database_module

@pytest_asyncio.fixture
async def test_engine():
    """Create a test engine for each test session using SQLite."""
    test_db_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(test_db_url, echo=False, future=True)
    
    # Create all tables upfront
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA foreign_keys=ON"))
        await conn.run_sync(Base.metadata.create_all)
    
    # Override the module-level engine so the app uses our test engine
    original_engine = database_module.engine
    original_session_maker = database_module.async_session_maker
    
    database_module.engine = engine
    database_module.async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    yield engine
    
    # Restore original engine
    database_module.engine = original_engine
    database_module.async_session_maker = original_session_maker
    
    await engine.dispose()


@pytest_asyncio.fixture
async def sample_team_node(isolated_session) -> TeamNode:
    node = TeamNode(founding_year=2000)
    isolated_session.add(node)
    await isolated_session.commit()
    await isolated_session.refresh(node)
    return node

@pytest_asyncio.fixture
async def another_team_node(isolated_session) -> TeamNode:
    node = TeamNode(founding_year=2010)
    isolated_session.add(node)
    await isolated_session.commit()
    await isolated_session.refresh(node)
    return node

@pytest_asyncio.fixture
async def sample_team_era(isolated_session, sample_team_node) -> TeamEra:
    era = TeamEra(node_id=sample_team_node.node_id, season_year=2001, registered_name="Test Era", tier_level=1)
    isolated_session.add(era)
    await isolated_session.commit()
    await isolated_session.refresh(era)
    return era

@pytest_asyncio.fixture
async def sample_lineage_event(isolated_session, sample_team_node, another_team_node) -> LineageEvent:
    event = LineageEvent(previous_node_id=sample_team_node.node_id, next_node_id=another_team_node.node_id, event_year=2015, event_type=EventType.LEGAL_TRANSFER)
    isolated_session.add(event)
    await isolated_session.commit()
    await isolated_session.refresh(event)
    return event

@pytest_asyncio.fixture
async def complex_lineage_tree(isolated_session) -> dict:
    # 3 generations: A -> B -> C, plus a split from B to D
    node_a = TeamNode(founding_year=1990)
    node_b = TeamNode(founding_year=2000)
    node_c = TeamNode(founding_year=2010)
    node_d = TeamNode(founding_year=2012)
    isolated_session.add_all([node_a, node_b, node_c, node_d])
    await isolated_session.commit()
    await isolated_session.refresh(node_a)
    await isolated_session.refresh(node_b)
    await isolated_session.refresh(node_c)
    await isolated_session.refresh(node_d)
    event_ab = LineageEvent(previous_node_id=node_a.node_id, next_node_id=node_b.node_id, event_year=2000, event_type=EventType.LEGAL_TRANSFER)
    event_bc = LineageEvent(previous_node_id=node_b.node_id, next_node_id=node_c.node_id, event_year=2010, event_type=EventType.LEGAL_TRANSFER)
    event_bd = LineageEvent(previous_node_id=node_b.node_id, next_node_id=node_d.node_id, event_year=2012, event_type=EventType.SPLIT)
    isolated_session.add_all([event_ab, event_bc, event_bd])
    await isolated_session.commit()
    return {
        "A": node_a,
        "B": node_b,
        "C": node_c,
        "D": node_d,
        "events": [event_ab, event_bc, event_bd],
    }
"""Pytest configuration and fixtures."""


@pytest_asyncio.fixture
async def client(isolated_session) -> AsyncGenerator[AsyncClient, None]:
    """Async test HTTP client with DB dependency overridden to use isolated_session."""

    async def _override_get_db():
        yield isolated_session

    # Override DB session to use test session
    app.dependency_overrides[get_db] = _override_get_db

    async def _override_checker(session: AsyncSession):
        # Always report connected in tests
        return True
    
    app.dependency_overrides[get_checker] = lambda: _override_checker
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_checker, None)


@pytest_asyncio.fixture
async def isolated_engine(test_engine):
    """Provide the shared test engine for tests."""
    yield test_engine


@pytest_asyncio.fixture
async def isolated_session(isolated_engine) -> AsyncGenerator[AsyncSession, None]:
    """Yield an isolated session bound to the test engine. Clears tables between tests."""
    # Clear all tables before test
    async with isolated_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    maker = async_sessionmaker(isolated_engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as session:
        yield session
    
    # Cleanup after test
    async with isolated_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(isolated_session) -> AsyncGenerator[AsyncSession, None]:
    """Alias for isolated_session for convenience."""
    yield isolated_session


@pytest_asyncio.fixture
async def test_client(isolated_session) -> AsyncGenerator[AsyncClient, None]:
    """Async test client with DB dependency overridden to use isolated_session."""

    async def _override_get_db():
        yield isolated_session

    # Override DB session and health checker to avoid external DB access
    app.dependency_overrides[get_db] = _override_get_db

    async def _override_checker(session: AsyncSession):
        # Always report connected in tests unless a test explicitly patches otherwise
        return True
    app.dependency_overrides[get_checker] = lambda: _override_checker
    try:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_checker, None)


@pytest_asyncio.fixture
async def sample_teams_in_db(isolated_session):
    """Create 5 teams with eras across different years and tiers."""
    nodes = []
    # Create 5 nodes
    for base_year in [1995, 2000, 2005, 2010, 2015]:
        node = TeamNode(founding_year=base_year)
        isolated_session.add(node)
        await isolated_session.flush()
        nodes.append(node)
    await isolated_session.commit()

    # Add eras with various years and tiers
    tier_cycle = [1, 2, 3, 2, 1]
    years = [2020, 2021, 2022, 2023, 2024]
    for i, node in enumerate(nodes):
        # Each node gets two eras in consecutive years
        e1 = TeamEra(
            node_id=node.node_id,
            season_year=years[i],
            registered_name=f"Team {i} A",
            tier_level=tier_cycle[i],
        )
        e2 = TeamEra(
            node_id=node.node_id,
            season_year=years[i] + 1,
            registered_name=f"Team {i} B",
            tier_level=tier_cycle[-(i+1)],
        )
        isolated_session.add_all([e1, e2])
    await isolated_session.commit()
    return nodes


# Auth fixtures
@pytest_asyncio.fixture
async def new_user(isolated_session) -> User:
    """Create a new user with NEW_USER role."""
    user = User(
        google_id="test_new_user_123",
        email="newuser@test.com",
        display_name="New User",
        role=UserRole.NEW_USER
    )
    isolated_session.add(user)
    await isolated_session.commit()
    await isolated_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def trusted_user(isolated_session) -> User:
    """Create a trusted user with TRUSTED_USER role."""
    user = User(
        google_id="test_trusted_user_123",
        email="trusteduser@test.com",
        display_name="Trusted User",
        role=UserRole.TRUSTED_USER,
        approved_edits_count=5
    )
    isolated_session.add(user)
    await isolated_session.commit()
    await isolated_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(isolated_session) -> User:
    """Create an admin user with ADMIN role."""
    user = User(
        google_id="test_admin_user_123",
        email="admin@test.com",
        display_name="Admin User",
        role=UserRole.ADMIN
    )
    isolated_session.add(user)
    await isolated_session.commit()
    await isolated_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def banned_user(isolated_session) -> User:
    """Create a banned user."""
    user = User(
        google_id="test_banned_user_123",
        email="banneduser@test.com",
        display_name="Banned User",
        role=UserRole.NEW_USER,
        is_banned=True,
        banned_reason="Test ban"
    )
    isolated_session.add(user)
    await isolated_session.commit()
    await isolated_session.refresh(user)
    return user


@pytest.fixture
def new_user_token(new_user: User) -> str:
    """Generate JWT token for new user."""
    return create_access_token({"sub": str(new_user.user_id)})


@pytest.fixture
def trusted_user_token(trusted_user: User) -> str:
    """Generate JWT token for trusted user."""
    return create_access_token({"sub": str(trusted_user.user_id)})


@pytest.fixture
def admin_user_token(admin_user: User) -> str:
    """Generate JWT token for admin user."""
    return create_access_token({"sub": str(admin_user.user_id)})


@pytest.fixture
def banned_user_token(banned_user: User) -> str:
    """Generate JWT token for banned user."""
    return create_access_token({"sub": str(banned_user.user_id)})


# Aliases for consistency with test files
@pytest_asyncio.fixture
async def async_session(isolated_session) -> AsyncSession:
    """Alias for isolated_session."""
    return isolated_session


@pytest_asyncio.fixture
async def test_user_new(new_user) -> User:
    """Alias for new_user."""
    return new_user


@pytest_asyncio.fixture
async def test_user_trusted(trusted_user) -> User:
    """Alias for trusted_user."""
    return trusted_user


@pytest_asyncio.fixture
async def test_user_admin(admin_user) -> User:
    """Alias for admin_user."""
    return admin_user


@pytest_asyncio.fixture
async def sample_teams(isolated_session):
    """Create sample teams with eras for testing merges."""
    nodes = []
    for i in range(3):
        node = TeamNode(founding_year=2000 + i * 5)
        isolated_session.add(node)
        await isolated_session.flush()
        
        # Add era for 2020
        era = TeamEra(
            node_id=node.node_id,
            season_year=2020,
            registered_name=f"Sample Team {i+1}",
            tier_level=(i % 3) + 1
        )
        isolated_session.add(era)
        nodes.append(node)
    
    await isolated_session.commit()
    for node in nodes:
        await isolated_session.refresh(node)
    return nodes
