from typing import List, Dict
from app.models.team import TeamNode, TeamEra
from app.models.lineage import LineageEvent
from app.services.dto import build_team_summary_dto, build_timeline_era_dto


class GraphBuilder:
    def build_jersey_composition(self, era: TeamEra) -> List[Dict]:
        sponsors = []
        for link in sorted(getattr(era, "sponsor_links", []), key=lambda l: getattr(l, "rank_order", 0)):
            brand = getattr(link, "brand", None)
            # Defensive: prefer default_hex_color, fallback to #4A90E2
            color = getattr(brand, "default_hex_color", None)
            if not color or not isinstance(color, str) or not color.startswith('#') or len(color) != 7:
                color = '#4A90E2'
            sponsors.append({
                "brand": brand.brand_name if brand else None,
                "color": color,
                "prominence": link.prominence_percent,
            })
        return sponsors

    def build_nodes(self, teams: List[TeamNode]) -> List[Dict]:
        nodes: List[Dict] = []
        for node in teams:
            # Build base node in snake_case for API schema
            base = {
                "id": str(getattr(node, "node_id", "")),
                "founding_year": getattr(node, "founding_year", None),
                "dissolution_year": getattr(node, "dissolution_year", None),
            }

            # Build eras aligned to TimelineEra schema
            eras: List[Dict] = []
            for era in getattr(node, "eras", []) or []:
                eras.append({
                    "year": getattr(era, "season_year", None),
                    "name": getattr(era, "registered_name", None),
                    "tier": getattr(era, "tier_level", None),
                    "sponsors": self.build_jersey_composition(era),
                })

            # Sort eras by year then name for deterministic ordering
            eras = sorted(eras, key=lambda e: (e.get("year") or 0, e.get("name") or ""))
            base["eras"] = eras
            nodes.append(base)

        # Deterministic node ordering: founding_year then id
        nodes = sorted(
            nodes,
            key=lambda n: (
                n.get("founding_year") if n.get("founding_year") is not None else -10**9,
                n.get("id") or "",
            ),
        )
        return nodes

    def build_links(self, events: List[LineageEvent]) -> List[Dict]:
        links: List[Dict] = []
        for ev in events:
            if ev.previous_node_id and ev.next_node_id:
                links.append({
                    "source": str(ev.previous_node_id),
                    "target": str(ev.next_node_id),
                    "year": ev.event_year,
                    "type": ev.event_type.name if hasattr(ev.event_type, 'name') else str(ev.event_type),
                })
        # Deterministic link ordering: year, source, target, type
        links = sorted(
            links,
            key=lambda l: (
                l.get("year") if l.get("year") is not None else -10**9,
                l.get("source") or "",
                l.get("target") or "",
                l.get("type") or "",
            ),
        )
        return links
