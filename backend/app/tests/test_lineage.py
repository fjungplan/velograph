import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.team import TeamNode
from app.models.lineage import LineageEvent
from app.models.enums import EventType
from app.services.lineage_service import LineageService
from app.core.exceptions import ValidationException

@pytest.mark.asyncio
async def test_create_legal_transfer_event(async_session: AsyncSession, sample_team_node):
    service = LineageService(async_session)
    event = await service.create_event(
        previous_id=sample_team_node.node_id,
        next_id=None,
        year=sample_team_node.founding_year + 1,
        event_type=EventType.LEGAL_TRANSFER,
        notes="Legal transfer test"
    )
    assert event.event_type == EventType.LEGAL_TRANSFER
    assert event.previous_node_id == sample_team_node.node_id

@pytest.mark.asyncio
async def test_create_merge_event(async_session: AsyncSession, sample_team_node, another_team_node):
    service = LineageService(async_session)
    # Create merge event with two previous nodes to same next node
    next_node = TeamNode(founding_year=2020)
    async_session.add(next_node)
    await async_session.commit()
    await async_session.refresh(next_node)
    event1 = await service.create_event(
        previous_id=sample_team_node.node_id,
        next_id=next_node.node_id,
        year=2021,
        event_type=EventType.MERGE,
        notes="Merge part 1"
    )
    event2 = await service.create_event(
        previous_id=another_team_node.node_id,
        next_id=next_node.node_id,
        year=2021,
        event_type=EventType.MERGE,
        notes="Merge part 2"
    )
    assert event1.next_node_id == next_node.node_id
    assert event2.next_node_id == next_node.node_id

@pytest.mark.asyncio
async def test_circular_reference_prevention(async_session: AsyncSession, sample_team_node):
    service = LineageService(async_session)
    with pytest.raises(ValidationException):
        await service.create_event(
            previous_id=sample_team_node.node_id,
            next_id=sample_team_node.node_id,
            year=2022,
            event_type=EventType.LEGAL_TRANSFER,
            notes="Should fail"
        )

@pytest.mark.asyncio
async def test_event_year_validation(async_session: AsyncSession, sample_team_node):
    service = LineageService(async_session)
    with pytest.raises(ValidationException):
        await service.create_event(
            previous_id=sample_team_node.node_id,
            next_id=None,
            year=sample_team_node.founding_year - 1,
            event_type=EventType.LEGAL_TRANSFER,
            notes="Invalid year"
        )

@pytest.mark.asyncio
async def test_relationship_traversal(async_session: AsyncSession, sample_team_node, another_team_node):
    service = LineageService(async_session)
    next_node = TeamNode(founding_year=2020)
    async_session.add(next_node)
    await async_session.commit()
    await async_session.refresh(next_node)
    await service.create_event(
        previous_id=sample_team_node.node_id,
        next_id=next_node.node_id,
        year=2021,
        event_type=EventType.LEGAL_TRANSFER,
        notes="Test traversal"
    )

    # Reload with eager relationships to avoid async lazy-load during assertions
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    stmt = (
        select(TeamNode)
        .where(TeamNode.node_id == next_node.node_id)
        .options(
            selectinload(TeamNode.incoming_events).selectinload(LineageEvent.previous_node),
            selectinload(TeamNode.outgoing_events).selectinload(LineageEvent.next_node),
        )
    )
    result = await async_session.execute(stmt)
    reloaded = result.scalar_one()

    pred_stmt = (
        select(TeamNode)
        .where(TeamNode.node_id == sample_team_node.node_id)
        .options(
            selectinload(TeamNode.outgoing_events).selectinload(LineageEvent.next_node),
            selectinload(TeamNode.incoming_events).selectinload(LineageEvent.previous_node),
        )
    )
    pred_result = await async_session.execute(pred_stmt)
    reloaded_predecessor = pred_result.scalar_one()

    assert [node.node_id for node in reloaded.get_predecessors()] == [sample_team_node.node_id]
    assert [node.node_id for node in reloaded_predecessor.get_successors()] == [reloaded.node_id]
