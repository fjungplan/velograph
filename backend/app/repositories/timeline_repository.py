from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.team import TeamEra, TeamNode
from app.models.sponsor import TeamSponsorLink
from app.models.lineage import LineageEvent


class TimelineRepository:
    """Repository for timeline queries with consolidated eager-loads.

    This initial stub centralizes the query shape used by TimelineService,
    preloading sponsor links/brands and adjacent lineage nodes to avoid async
    lazy-loads during serialization.
    """

    async def fetch_eras_and_events(
        self,
        session: AsyncSession,
        *,
        year: int | None = None,
        tier: int | None = None,
    ) -> tuple[list[TeamEra], list[LineageEvent]]:
        era_stmt = (
            select(TeamEra)
            .options(
                selectinload(TeamEra.node),
                selectinload(TeamEra.sponsor_links).selectinload(TeamSponsorLink.brand),
            )
        )
        if year is not None:
            era_stmt = era_stmt.where(TeamEra.season_year == year)
        if tier is not None:
            era_stmt = era_stmt.where(TeamEra.tier_level == tier)

        event_stmt = (
            select(LineageEvent)
            .options(
                selectinload(LineageEvent.previous_node).selectinload(TeamNode.eras)
                .selectinload(TeamEra.sponsor_links).selectinload(TeamSponsorLink.brand),
                selectinload(LineageEvent.next_node).selectinload(TeamNode.eras)
                .selectinload(TeamEra.sponsor_links).selectinload(TeamSponsorLink.brand),
            )
        )
        if year is not None:
            event_stmt = event_stmt.where(LineageEvent.event_year == year)

        eras = list((await session.execute(era_stmt)).scalars().all())
        events = list((await session.execute(event_stmt)).scalars().all())
        return eras, events
