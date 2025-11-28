from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.team import TeamNode, TeamEra
from app.models.lineage import LineageEvent
from app.core.graph_builder import GraphBuilder


class TimelineService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.builder = GraphBuilder()

    async def get_graph_data(
        self,
        start_year: int,
        end_year: int,
        include_dissolved: bool,
        tier_filter: Optional[List[int]] = None,
    ) -> Dict:
        nodes_query = (
            select(TeamNode)
            .options(
                selectinload(TeamNode.eras).selectinload(TeamEra.sponsor_links).selectinload(
                    TeamEra.sponsor_links.property.mapper.class_.brand  # type: ignore
                ),
                selectinload(TeamNode.outgoing_events),
                selectinload(TeamNode.incoming_events),
            )
        )

        # filter dissolved
        if not include_dissolved:
            nodes_query = nodes_query.where((TeamNode.dissolution_year.is_(None)) | (TeamNode.dissolution_year > end_year))

        result = await self.session.execute(nodes_query)
        teams: List[TeamNode] = list(result.scalars().all())

        # filter eras by year and tier
        for node in teams:
            node.eras = [
                era for era in node.eras
                if (start_year <= era.season_year <= end_year) and (tier_filter is None or (era.tier_level in tier_filter))
            ]

        # lineage events within range
        events_result = await self.session.execute(
            select(LineageEvent)
            .where((LineageEvent.event_year >= start_year) & (LineageEvent.event_year <= end_year))
        )
        events: List[LineageEvent] = list(events_result.scalars().all())

        nodes = self.builder.build_nodes(teams)
        links = self.builder.build_links(events)

        meta = {
            "year_range": [start_year, end_year],
            "node_count": len(nodes),
            "link_count": len(links),
        }
        return {"nodes": nodes, "links": links, "meta": meta}
