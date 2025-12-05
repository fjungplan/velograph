"""Tests for merge event functionality."""
import pytest
from datetime import datetime
from uuid import uuid4

from app.models.edit import EditType, EditStatus
from app.models.enums import EventType
from app.models.user import UserRole


@pytest.mark.asyncio
async def test_create_merge_basic(async_session, test_user_trusted, sample_teams):
    """Test basic merge with 2 teams."""
    from app.services.edit_service import EditService
    from app.schemas.edits import MergeEventRequest
    from app.models.team import TeamNode
    from app.models.lineage import LineageEvent
    
    # Get two teams
    team_a = sample_teams[0]
    team_b = sample_teams[1]
    
    request = MergeEventRequest(
        source_node_ids=[str(team_a.node_id), str(team_b.node_id)],
        merge_year=2020,
        new_team_name="United Team",
        new_team_tier=1,
        reason="Both teams merged to form a stronger organization"
    )
    
    result = await EditService.create_merge_edit(
        async_session,
        test_user_trusted,
        request
    )
    
    # Check result
    assert result.status == "APPROVED"
    assert "successfully" in result.message.lower()
    
    # Verify source nodes are dissolved
    await async_session.refresh(team_a)
    await async_session.refresh(team_b)
    assert team_a.dissolution_year == 2020
    assert team_b.dissolution_year == 2020
    
    # Verify new node was created
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    stmt = select(TeamNode).where(TeamNode.founding_year == 2020).options(selectinload(TeamNode.eras))
    result_nodes = await async_session.execute(stmt)
    new_nodes = result_nodes.scalars().all()
    
    # Find the newly created node (not one of the original teams)
    new_node = None
    for node in new_nodes:
        if node.node_id not in [team_a.node_id, team_b.node_id]:
            new_node = node
            break
    
    assert new_node is not None
    assert len(new_node.eras) == 1
    assert new_node.eras[0].registered_name == "United Team"
    assert new_node.eras[0].tier_level == 1
    
    # Verify lineage events were created
    stmt = select(LineageEvent).where(LineageEvent.next_node_id == new_node.node_id)
    result_events = await async_session.execute(stmt)
    events = result_events.scalars().all()
    
    assert len(events) == 2
    assert all(e.event_type == EventType.MERGE for e in events)
    assert all(e.event_year == 2020 for e in events)


@pytest.mark.asyncio
async def test_create_merge_five_teams(isolated_session, test_user_admin):
    """Test merge with maximum 5 teams."""
    from app.services.edit_service import EditService
    from app.schemas.edits import MergeEventRequest
    from app.models.team import TeamNode, TeamEra
    
    # Create 5 teams
    teams = []
    for i in range(5):
        node = TeamNode(founding_year=2010)
        isolated_session.add(node)
        await isolated_session.flush()
        
        era = TeamEra(
            node_id=node.node_id,
            season_year=2015,
            registered_name=f"Team {i+1}",
            tier_level=1
        )
        isolated_session.add(era)
        teams.append(node)
    
    await isolated_session.commit()
    
    request = MergeEventRequest(
        source_node_ids=[str(t.node_id) for t in teams],
        merge_year=2015,
        new_team_name="Mega Team",
        new_team_tier=1,
        reason="Five teams united to create a superteam"
    )
    
    result = await EditService.create_merge_edit(
        isolated_session,
        test_user_admin,
        request
    )
    
    assert result.status == "APPROVED"
    
    # Verify all 5 nodes are dissolved
    for team in teams:
        await isolated_session.refresh(team)
        assert team.dissolution_year == 2015


@pytest.mark.asyncio
async def test_merge_validation_too_few_teams(async_session, test_user_trusted, sample_teams):
    """Test merge validation: requires at least 2 teams."""
    from app.schemas.edits import MergeEventRequest
    from pydantic import ValidationError
    
    with pytest.raises(ValidationError) as exc_info:
        MergeEventRequest(
            source_node_ids=[str(sample_teams[0].node_id)],
            merge_year=2020,
            new_team_name="Solo Team",
            new_team_tier=1,
            reason="Cannot merge a single team"
        )
    
    assert "at least 2 source teams" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_merge_validation_too_many_teams(async_session, test_user_trusted):
    """Test merge validation: maximum 5 teams."""
    from app.schemas.edits import MergeEventRequest
    from pydantic import ValidationError
    
    with pytest.raises(ValidationError) as exc_info:
        MergeEventRequest(
            source_node_ids=[str(uuid4()) for _ in range(6)],
            merge_year=2020,
            new_team_name="Too Many Teams",
            new_team_tier=1,
            reason="Trying to merge 6 teams"
        )
    
    assert "cannot merge more than 5 teams" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_merge_validation_invalid_year(async_session, test_user_trusted, sample_teams):
    """Test merge validation: year must be valid."""
    from app.schemas.edits import MergeEventRequest
    from pydantic import ValidationError
    
    # Test year too early
    with pytest.raises(ValidationError):
        MergeEventRequest(
            source_node_ids=[str(sample_teams[0].node_id), str(sample_teams[1].node_id)],
            merge_year=1800,
            new_team_name="Old Team",
            new_team_tier=1,
            reason="Invalid year"
        )
    
    # Test year too late
    with pytest.raises(ValidationError):
        MergeEventRequest(
            source_node_ids=[str(sample_teams[0].node_id), str(sample_teams[1].node_id)],
            merge_year=2100,
            new_team_name="Future Team",
            new_team_tier=1,
            reason="Invalid year"
        )


@pytest.mark.asyncio
async def test_merge_nonexistent_team(async_session, test_user_trusted, sample_teams):
    """Test merge with nonexistent team."""
    from app.services.edit_service import EditService
    from app.schemas.edits import MergeEventRequest
    
    fake_id = str(uuid4())
    request = MergeEventRequest(
        source_node_ids=[str(sample_teams[0].node_id), fake_id],
        merge_year=2020,
        new_team_name="United Team",
        new_team_tier=1,
        reason="Merging with fake team"
    )
    
    with pytest.raises(ValueError) as exc_info:
        await EditService.create_merge_edit(
            async_session,
            test_user_trusted,
            request
        )
    
    assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_merge_team_not_active_in_year(async_session, test_user_trusted, sample_teams):
    """Test merge validation: teams must be active in merge year."""
    from app.services.edit_service import EditService
    from app.schemas.edits import MergeEventRequest
    
    team_a = sample_teams[0]
    team_b = sample_teams[1]
    
    request = MergeEventRequest(
        source_node_ids=[str(team_a.node_id), str(team_b.node_id)],
        merge_year=1990,  # Teams don't have eras in 1990
        new_team_name="United Team",
        new_team_tier=1,
        reason="Trying to merge in wrong year"
    )
    
    with pytest.raises(ValueError) as exc_info:
        await EditService.create_merge_edit(
            async_session,
            test_user_trusted,
            request
        )
    
    assert "not active" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_merge_pending_for_new_user(async_session, test_user_new, sample_teams):
    """Test merge goes to moderation queue for new users."""
    from app.services.edit_service import EditService
    from app.schemas.edits import MergeEventRequest
    from app.models.edit import Edit
    from sqlalchemy import select
    
    team_a = sample_teams[0]
    team_b = sample_teams[1]
    
    request = MergeEventRequest(
        source_node_ids=[str(team_a.node_id), str(team_b.node_id)],
        merge_year=2020,
        new_team_name="United Team",
        new_team_tier=1,
        reason="New user submitting merge"
    )
    
    result = await EditService.create_merge_edit(
        async_session,
        test_user_new,
        request
    )
    
    assert result.status == "PENDING"
    assert "moderation" in result.message.lower()
    
    # Verify edit was created but not applied
    stmt = select(Edit).where(Edit.edit_id == result.edit_id)
    edit_result = await async_session.execute(stmt)
    edit = edit_result.scalar_one()
    
    assert edit.status == EditStatus.PENDING
    assert edit.edit_type == EditType.MERGE
    
    # Verify nodes were NOT dissolved (merge not applied yet)
    await async_session.refresh(team_a)
    await async_session.refresh(team_b)
    assert team_a.dissolution_year is None
    assert team_b.dissolution_year is None


@pytest.mark.asyncio
async def test_merge_manual_override_flag(async_session, test_user_trusted, sample_teams):
    """Test that merged team has manual override flag set."""
    from app.services.edit_service import EditService
    from app.schemas.edits import MergeEventRequest
    from app.models.team import TeamNode
    from sqlalchemy import select
    
    team_a = sample_teams[0]
    team_b = sample_teams[1]
    
    request = MergeEventRequest(
        source_node_ids=[str(team_a.node_id), str(team_b.node_id)],
        merge_year=2020,
        new_team_name="United Team",
        new_team_tier=1,
        reason="Testing manual override"
    )
    
    await EditService.create_merge_edit(
        async_session,
        test_user_trusted,
        request
    )
    
    # Find the new team
    from sqlalchemy.orm import selectinload
    stmt = select(TeamNode).where(TeamNode.founding_year == 2020).options(selectinload(TeamNode.eras))
    result = await async_session.execute(stmt)
    new_nodes = result.scalars().all()
    
    new_node = None
    for node in new_nodes:
        if node.node_id not in [team_a.node_id, team_b.node_id]:
            new_node = node
            break
    
    assert new_node is not None
    assert new_node.eras[0].is_manual_override is True
    assert f"user_{test_user_trusted.user_id}" in new_node.eras[0].source_origin


@pytest.mark.asyncio
async def test_merge_validation_team_name_too_short(async_session, test_user_trusted, sample_teams):
    """Test merge validation: team name must be at least 3 characters."""
    from app.schemas.edits import MergeEventRequest
    from pydantic import ValidationError
    
    with pytest.raises(ValidationError) as exc_info:
        MergeEventRequest(
            source_node_ids=[str(sample_teams[0].node_id), str(sample_teams[1].node_id)],
            merge_year=2020,
            new_team_name="AB",
            new_team_tier=1,
            reason="Testing short name"
        )
    
    assert "at least 3 characters" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_merge_validation_team_name_too_long(async_session, test_user_trusted, sample_teams):
    """Test merge validation: team name cannot exceed 200 characters."""
    from app.schemas.edits import MergeEventRequest
    from pydantic import ValidationError
    
    with pytest.raises(ValidationError) as exc_info:
        MergeEventRequest(
            source_node_ids=[str(sample_teams[0].node_id), str(sample_teams[1].node_id)],
            merge_year=2020,
            new_team_name="A" * 201,
            new_team_tier=1,
            reason="Testing long name"
        )
    
    assert "cannot exceed 200 characters" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_merge_validation_reason_too_short(async_session, test_user_trusted, sample_teams):
    """Test merge validation: reason must be at least 10 characters."""
    from app.schemas.edits import MergeEventRequest
    from pydantic import ValidationError
    
    with pytest.raises(ValidationError) as exc_info:
        MergeEventRequest(
            source_node_ids=[str(sample_teams[0].node_id), str(sample_teams[1].node_id)],
            merge_year=2020,
            new_team_name="United Team",
            new_team_tier=1,
            reason="Short"
        )
    
    assert "at least 10 characters" in str(exc_info.value).lower()
