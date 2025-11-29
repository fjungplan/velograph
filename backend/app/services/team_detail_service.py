from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.team import TeamNode, TeamEra
from app.models.lineage import LineageEvent
from app.models.enums import EventType
from app.schemas.team_detail import (
    TeamHistoryResponse,
    TeamHistoryEra,
    LineageSummary,
    TransitionInfo,
)


class TeamDetailService:
    @staticmethod
    async def get_team_history(session: AsyncSession, node_id: str) -> Optional[TeamHistoryResponse]:
        stmt = (
            select(TeamNode)
            .where(TeamNode.node_id == node_id)
            .options(
                selectinload(TeamNode.eras),
                selectinload(TeamNode.incoming_events)
                .selectinload(LineageEvent.previous_node)
                .selectinload(TeamNode.eras),
                selectinload(TeamNode.outgoing_events)
                .selectinload(LineageEvent.next_node)
                .selectinload(TeamNode.eras),
            )
        )
        result = await session.execute(stmt)
        team: Optional[TeamNode] = result.scalar_one_or_none()
        if not team:
            return None

        eras_sorted = sorted(team.eras, key=lambda e: e.season_year)
        current_year = datetime.utcnow().year

        timeline: List[TeamHistoryEra] = []
        for era in eras_sorted:
            status = TeamDetailService.calculate_era_status(
                era, current_year, team.dissolution_year
            )
            predecessor = TeamDetailService._find_predecessor_event(team, era)
            successor = TeamDetailService._find_successor_event(team, era)
            timeline.append(
                TeamHistoryEra(
                    year=era.season_year,
                    name=era.registered_name,
                    tier=era.tier_level,
                    uci_code=era.uci_code,
                    status=status,
                    predecessor=predecessor,
                    successor=successor,
                )
            )

        lineage_summary = LineageSummary(
            has_predecessors=len(team.incoming_events) > 0,
            has_successors=len(team.outgoing_events) > 0,
            spiritual_succession=any(e.event_type == EventType.SPIRITUAL_SUCCESSION for e in team.incoming_events)
            or any(e.event_type == EventType.SPIRITUAL_SUCCESSION for e in team.outgoing_events),
        )

        return TeamHistoryResponse(
            node_id=str(team.node_id),
            founding_year=team.founding_year,
            dissolution_year=team.dissolution_year,
            timeline=timeline,
            lineage_summary=lineage_summary,
        )

    @staticmethod
    def calculate_era_status(
        era: TeamEra, current_year: int, dissolution_year: Optional[int]
    ) -> str:
        if dissolution_year is not None and era.season_year >= dissolution_year:
            return "dissolved"
        if era.season_year == current_year and dissolution_year is None:
            return "active"
        if era.season_year < current_year:
            return "historical"
        return "active"

    @staticmethod
    def _event_to_transition(event: LineageEvent, name: str) -> TransitionInfo:
        return TransitionInfo(
            year=event.event_year,
            name=name,
            event_type=TeamDetailService._classify_transition(event),
        )

    @staticmethod
    def _classify_transition(event: LineageEvent) -> str:
        if event.event_type == EventType.MERGE:
            return "MERGED_INTO"
        if event.event_type == EventType.SPIRITUAL_SUCCESSION:
            return "REVIVAL"
        if event.event_type == EventType.LEGAL_TRANSFER:
            return "ACQUISITION"
        if event.event_type == EventType.SPLIT:
            return "SPLIT"
        return str(event.event_type)

    @staticmethod
    def _find_predecessor_event(team: TeamNode, era: TeamEra) -> Optional[TransitionInfo]:
        # predecessor: incoming event targeting this node with same or previous year
        candidates = [e for e in team.incoming_events if e.event_year <= era.season_year]
        if not candidates:
            return None
        event = max(candidates, key=lambda e: e.event_year)
        name = None
        if event.previous_node and event.previous_node.eras:
            prev_eras = sorted(event.previous_node.eras, key=lambda x: x.season_year)
            name = prev_eras[-1].registered_name
        return TeamDetailService._event_to_transition(event, name or "")

    @staticmethod
    def _find_successor_event(team: TeamNode, era: TeamEra) -> Optional[TransitionInfo]:
        # successor: outgoing event from this node after or at era year
        candidates = [e for e in team.outgoing_events if e.event_year >= era.season_year]
        if not candidates:
            return None
        event = min(candidates, key=lambda e: e.event_year)
        name = None
        if event.next_node and event.next_node.eras:
            next_eras = sorted(event.next_node.eras, key=lambda x: x.season_year)
            name = next_eras[0].registered_name
        return TeamDetailService._event_to_transition(event, name or "")
