"""Service layer for TeamNode and TeamEra operations."""
from __future__ import annotations

from typing import List, Optional
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.team import TeamNode, TeamEra
from app.core.exceptions import (
    NodeNotFoundException,
    DuplicateEraException,
    ValidationException,
)
from app.services.timeline_service import TimelineService
from app.repositories.team_repository import TeamRepository


class TeamService:
    """Encapsulates business logic for team node and era management."""

    @staticmethod
    async def get_node_with_eras(session: AsyncSession, node_id: uuid.UUID) -> TeamNode:
        # Use repository to ensure consistent eager-loading of eras and sponsors
        node = await TeamRepository.get_by_id(session, node_id)
        if not node:
            # SELECT may begin a transaction implicitly; rollback to clear state
            await session.rollback()
            raise NodeNotFoundException(f"TeamNode {node_id} not found")
        # Defensive: avoid async lazy-load by ensuring eras are present in instance dict
        if 'eras' not in node.__dict__:
            # Fetch eras via repository with eager-loaded sponsors
            eras = await TeamRepository.get_eras_for_node(session, node_id)
            node.__dict__['eras'] = eras
        return node

    @staticmethod
    async def get_eras_by_year(session: AsyncSession, year: int) -> List[TeamEra]:
        if year < 1900 or year > 2100:
            raise ValidationException(f"Year {year} out of allowed range (1900-2100)")
        # Delegate to repository to keep eager-loading consistent
        stmt = select(TeamEra).where(TeamEra.season_year == year)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def list_nodes(
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 50,
        active_in_year: Optional[int] = None,
        tier_level: Optional[int] = None,
    ) -> tuple[List[TeamNode], int]:
        # Use repository to handle filtering, pagination, and eager-loading
        nodes, total = await TeamRepository.get_all(
            session,
            skip=skip,
            limit=limit,
            active_in_year=active_in_year,
            tier_level=tier_level,
        )
        # Defensive: ensure eras are attached to each node to avoid async lazy-loads later
        for n in nodes:
            if 'eras' not in n.__dict__:
                eras = await TeamRepository.get_eras_for_node(session, n.node_id)
                n.__dict__['eras'] = eras
        return nodes, total

    @staticmethod
    async def get_node_eras(
        session: AsyncSession,
        node_id: uuid.UUID,
        *,
        year_filter: Optional[int] = None,
    ) -> List[TeamEra]:
        # Delegate to repository to apply eager-loading consistently
        return await TeamRepository.get_eras_for_node(
            session, node_id, year_filter=year_filter
        )

    @staticmethod
    async def create_era(
        session: AsyncSession,
        node_id: uuid.UUID,
        year: int,
        registered_name: str,
        *,
        uci_code: Optional[str] = None,
        tier_level: Optional[int] = None,
        source_origin: Optional[str] = None,
        is_manual_override: bool = False,
    ) -> TeamEra:
        # Basic input validations BEFORE any DB I/O
        if year < 1900 or year > 2100:
            raise ValidationException("season_year must be between 1900 and 2100")
        if tier_level is not None and tier_level not in (1, 2, 3):
            raise ValidationException("tier_level must be 1, 2, or 3 when provided")
        if uci_code is not None and (
            len(uci_code) != 3 or not uci_code.isalpha() or not uci_code.isupper()
        ):
            raise ValidationException("uci_code must be exactly 3 uppercase letters")
        if not registered_name or registered_name.strip() == "":
            raise ValidationException("registered_name cannot be empty")

        # Ensure node exists (DB I/O begins here)
        node_stmt = select(TeamNode).where(TeamNode.node_id == node_id)
        node_result = await session.execute(node_stmt)
        node = node_result.scalar_one_or_none()
        if not node:
            await session.rollback()
            raise NodeNotFoundException(f"TeamNode {node_id} not found")

        # Duplicate check
        dup_stmt = select(TeamEra).where(
            TeamEra.node_id == node_id, TeamEra.season_year == year
        )
        dup_result = await session.execute(dup_stmt)
        if dup_result.scalar_one_or_none():
            await session.rollback()
            raise DuplicateEraException(
                f"Era for node {node_id} and year {year} already exists"
            )

        era = TeamEra(
            node_id=node_id,
            season_year=year,
            registered_name=registered_name.strip(),
            uci_code=uci_code,
            tier_level=tier_level,
            source_origin=source_origin,
            is_manual_override=is_manual_override,
        )
        session.add(era)
        await session.commit()
        # Invalidate timeline cache after data change
        TimelineService.invalidate_cache()
        await session.refresh(era)
        return era
