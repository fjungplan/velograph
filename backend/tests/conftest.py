import pytest
import pytest_asyncio
from httpx import AsyncClient
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.db.base import Base
from app.core.config import settings
from main import app
from app.models.team import TeamNode, TeamEra
from app.models.lineage import LineageEvent
from app.models.enums import EventType
import uuid

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
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async test HTTP client for the FastAPI app (starts lifespan)."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def isolated_engine():
    """Provide a fresh async engine per test using in-memory SQLite (no Postgres required)."""
    test_db_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(test_db_url, echo=False, future=True)
    # Create all tables for models
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA foreign_keys=ON"))
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def isolated_session(isolated_engine) -> AsyncGenerator[AsyncSession, None]:
    """Yield an isolated session bound to a fresh engine for DB tests."""
    maker = async_sessionmaker(isolated_engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as session:
        yield session


@pytest_asyncio.fixture
async def db_session(isolated_session) -> AsyncGenerator[AsyncSession, None]:
    """Alias for isolated_session for convenience."""
    yield isolated_session
