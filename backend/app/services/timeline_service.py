from typing import Dict, List, Optional, Tuple
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.team import TeamNode, TeamEra
from app.models.lineage import LineageEvent
from app.repositories.timeline_repository import TimelineRepository
from app.core.graph_builder import GraphBuilder
from app.core.config import settings


class TimelineService:
    # Simple in-memory cache: key -> (expires_at, value)
    _cache: Dict[str, Tuple[float, Dict]] = {}
    _CACHE_TTL_SECONDS: int = 300  # 5 minutes

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
        # Cache key based on query parameters
        key_parts = [
            f"start:{start_year}",
            f"end:{end_year}",
            f"dissolved:{include_dissolved}",
            f"tiers:{','.join(map(str, tier_filter))}" if tier_filter else "tiers:"
        ]
        cache_key = "timeline:" + "|".join(key_parts)

        now = time.time()
        if settings.TIMELINE_CACHE_ENABLED:
            cached = self._cache.get(cache_key)
            if cached and cached[0] > now:
                return cached[1]

        repo = TimelineRepository()
        eras, events = await repo.fetch_eras_and_events(
            self.session,
            year=None,  # we'll filter by range below
            tier=None,
        )

        # Build team nodes from eras, applying filters and dissolved policy
        # Group eras by node
        nodes_by_id: Dict[str, TeamNode] = {}
        for era in eras:
            if not (start_year <= era.season_year <= end_year):
                continue
            if tier_filter is not None and era.tier_level not in tier_filter:
                continue
            node = era.node
            if not include_dissolved and node.dissolution_year is not None and node.dissolution_year <= end_year:
                continue
            if str(node.node_id) not in nodes_by_id:
                nodes_by_id[str(node.node_id)] = node
                # Avoid triggering lazy load when clearing eras
                node.__dict__['eras'] = []
            nodes_by_id[str(node.node_id)].eras.append(era)
        teams = list(nodes_by_id.values())

        # Filter events to range
        events = [e for e in events if (start_year <= e.event_year <= end_year)]

        nodes = self.builder.build_nodes(teams)
        links = self.builder.build_links(events)

        meta = {
            "year_range": [start_year, end_year],
            "node_count": len(nodes),
            "link_count": len(links),
        }
        result = {"nodes": nodes, "links": links, "meta": meta}
        # Store in cache
        if settings.TIMELINE_CACHE_ENABLED:
            ttl = getattr(settings, "TIMELINE_CACHE_TTL_SECONDS", self._CACHE_TTL_SECONDS)
            self._cache[cache_key] = (now + ttl, result)
        return result

    @classmethod
    def invalidate_cache(cls) -> None:
        """Invalidate all cached timeline results."""
        cls._cache.clear()
