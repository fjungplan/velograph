import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.team import TeamNode, TeamEra
from app.models.edit import Edit, EditType, EditStatus
from datetime import datetime


@pytest.mark.asyncio
async def test_edit_metadata_as_new_user(test_client: AsyncClient, db_session: AsyncSession, new_user_token: str):
    """Test that new users' edits go to moderation queue"""
    # Create a team node and era
    node = TeamNode(founding_year=2000)
    db_session.add(node)
    await db_session.flush()
    
    era = TeamEra(
        node_id=node.node_id,
        season_year=2000,
        registered_name="Test Team",
        uci_code="TST",
        tier_level=1
    )
    db_session.add(era)
    await db_session.commit()
    
    # Submit edit
    response = await test_client.post(
        "/api/v1/edits/metadata",
        json={
            "era_id": str(era.era_id),
            "registered_name": "Updated Test Team",
            "reason": "This is a valid reason for the change"
        },
        headers={"Authorization": f"Bearer {new_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PENDING"
    assert "moderation" in data["message"].lower()
    
    # Verify edit record was created
    await db_session.refresh(era)
    assert era.registered_name == "Test Team"  # Not changed yet
    assert not era.is_manual_override  # Not marked as override yet


@pytest.mark.asyncio
async def test_edit_metadata_as_trusted_user(test_client: AsyncClient, db_session: AsyncSession, trusted_user_token: str, trusted_user: User):
    """Test that trusted users' edits are auto-approved"""
    # Create a team node and era
    node = TeamNode(founding_year=2000)
    db_session.add(node)
    await db_session.flush()
    
    era = TeamEra(
        node_id=node.node_id,
        season_year=2000,
        registered_name="Test Team",
        uci_code="TST",
        tier_level=1
    )
    db_session.add(era)
    await db_session.commit()
    
    initial_edit_count = trusted_user.approved_edits_count
    
    # Submit edit
    response = await test_client.post(
        "/api/v1/edits/metadata",
        json={
            "era_id": str(era.era_id),
            "registered_name": "Updated Test Team",
            "uci_code": "UPD",
            "tier_level": 2,
            "reason": "This is a valid reason for the change"
        },
        headers={"Authorization": f"Bearer {trusted_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "APPROVED"
    assert "immediately" in data["message"].lower()
    
    # Verify changes were applied
    await db_session.refresh(era)
    assert era.registered_name == "Updated Test Team"
    assert era.uci_code == "UPD"
    assert era.tier_level == 2
    assert era.is_manual_override is True
    assert era.source_origin == f"user_{trusted_user.user_id}"
    
    # Verify edit count incremented
    await db_session.refresh(trusted_user)
    assert trusted_user.approved_edits_count == initial_edit_count + 1


@pytest.mark.asyncio
async def test_edit_metadata_validation_uci_code(test_client: AsyncClient, db_session: AsyncSession, trusted_user_token: str):
    """Test UCI code validation"""
    node = TeamNode(founding_year=2000)
    db_session.add(node)
    await db_session.flush()
    
    era = TeamEra(
        node_id=node.node_id,
        season_year=2000,
        registered_name="Test Team",
        tier_level=1
    )
    db_session.add(era)
    await db_session.commit()
    
    # Test invalid UCI code (too long)
    response = await test_client.post(
        "/api/v1/edits/metadata",
        json={
            "era_id": str(era.era_id),
            "uci_code": "TOOLONG",
            "reason": "This is a valid reason"
        },
        headers={"Authorization": f"Bearer {trusted_user_token}"}
    )
    assert response.status_code == 422
    
    # Test invalid UCI code (lowercase)
    response = await test_client.post(
        "/api/v1/edits/metadata",
        json={
            "era_id": str(era.era_id),
            "uci_code": "abc",
            "reason": "This is a valid reason"
        },
        headers={"Authorization": f"Bearer {trusted_user_token}"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_edit_metadata_validation_tier_level(test_client: AsyncClient, db_session: AsyncSession, trusted_user_token: str):
    """Test tier level validation"""
    node = TeamNode(founding_year=2000)
    db_session.add(node)
    await db_session.flush()
    
    era = TeamEra(
        node_id=node.node_id,
        season_year=2000,
        registered_name="Test Team",
        tier_level=1
    )
    db_session.add(era)
    await db_session.commit()
    
    # Test invalid tier level
    response = await test_client.post(
        "/api/v1/edits/metadata",
        json={
            "era_id": str(era.era_id),
            "tier_level": 4,
            "reason": "This is a valid reason"
        },
        headers={"Authorization": f"Bearer {trusted_user_token}"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_edit_metadata_validation_reason_too_short(test_client: AsyncClient, db_session: AsyncSession, trusted_user_token: str):
    """Test reason minimum length validation"""
    node = TeamNode(founding_year=2000)
    db_session.add(node)
    await db_session.flush()
    
    era = TeamEra(
        node_id=node.node_id,
        season_year=2000,
        registered_name="Test Team",
        tier_level=1
    )
    db_session.add(era)
    await db_session.commit()
    
    # Test reason too short
    response = await test_client.post(
        "/api/v1/edits/metadata",
        json={
            "era_id": str(era.era_id),
            "registered_name": "New Name",
            "reason": "Short"
        },
        headers={"Authorization": f"Bearer {trusted_user_token}"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_edit_metadata_no_changes(test_client: AsyncClient, db_session: AsyncSession, trusted_user_token: str):
    """Test that edit with no changes is rejected"""
    node = TeamNode(founding_year=2000)
    db_session.add(node)
    await db_session.flush()
    
    era = TeamEra(
        node_id=node.node_id,
        season_year=2000,
        registered_name="Test Team",
        tier_level=1
    )
    db_session.add(era)
    await db_session.commit()
    
    # Submit edit with no actual changes
    response = await test_client.post(
        "/api/v1/edits/metadata",
        json={
            "era_id": str(era.era_id),
            "reason": "This is a valid reason"
        },
        headers={"Authorization": f"Bearer {trusted_user_token}"}
    )
    
    assert response.status_code == 400
    assert "no changes" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_edit_metadata_era_not_found(test_client: AsyncClient, trusted_user_token: str):
    """Test edit with non-existent era"""
    response = await test_client.post(
        "/api/v1/edits/metadata",
        json={
            "era_id": "00000000-0000-0000-0000-000000000000",
            "registered_name": "New Name",
            "reason": "This is a valid reason"
        },
        headers={"Authorization": f"Bearer {trusted_user_token}"}
    )
    
    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_edit_metadata_unauthorized(test_client: AsyncClient, db_session: AsyncSession):
    """Test edit without authentication"""
    node = TeamNode(founding_year=2000)
    db_session.add(node)
    await db_session.flush()
    
    era = TeamEra(
        node_id=node.node_id,
        season_year=2000,
        registered_name="Test Team",
        tier_level=1
    )
    db_session.add(era)
    await db_session.commit()
    
    response = await test_client.post(
        "/api/v1/edits/metadata",
        json={
            "era_id": str(era.era_id),
            "registered_name": "New Name",
            "reason": "This is a valid reason"
        }
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_edit_metadata_banned_user(test_client: AsyncClient, db_session: AsyncSession, banned_user_token: str):
    """Test that banned users cannot edit"""
    node = TeamNode(founding_year=2000)
    db_session.add(node)
    await db_session.flush()
    
    era = TeamEra(
        node_id=node.node_id,
        season_year=2000,
        registered_name="Test Team",
        tier_level=1
    )
    db_session.add(era)
    await db_session.commit()
    
    response = await test_client.post(
        "/api/v1/edits/metadata",
        json={
            "era_id": str(era.era_id),
            "registered_name": "New Name",
            "reason": "This is a valid reason"
        },
        headers={"Authorization": f"Bearer {banned_user_token}"}
    )
    
    assert response.status_code == 403
    assert "banned" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_manual_override_prevents_scraper_overwrite(db_session: AsyncSession, trusted_user: User):
    """Test that manual override flag is set correctly"""
    node = TeamNode(founding_year=2000)
    db_session.add(node)
    await db_session.flush()
    
    era = TeamEra(
        node_id=node.node_id,
        season_year=2000,
        registered_name="Test Team",
        tier_level=1,
        source_origin="scraper_pcs"
    )
    db_session.add(era)
    await db_session.commit()
    
    assert not era.is_manual_override
    assert era.source_origin == "scraper_pcs"
    
    # Apply manual edit
    from app.services.edit_service import EditService
    await EditService._apply_metadata_changes(
        db_session,
        era,
        {"registered_name": "Manually Updated Team"},
        trusted_user
    )
    
    await db_session.refresh(era)
    assert era.is_manual_override is True
    assert era.source_origin == f"user_{trusted_user.user_id}"
    assert era.registered_name == "Manually Updated Team"
