from typing import List, Dict
from app.models.team import TeamNode, TeamEra
from app.models.lineage import LineageEvent
from app.services.dto import build_timeline_era_dto, build_team_summary_dto


class GraphBuilder:
    def build_jersey_composition(self, era: TeamEra) -> List[Dict]:
        # Kept for backward compatibility if used elsewhere; DTO now handles sponsors.
        sponsors = []
        for link in getattr(era, "sponsors_ordered", []) or []:
            brand = getattr(link, "brand", None)
            sponsors.append({
                "brand": brand.brand_name if brand else None,
                "color": getattr(brand, "color_hex", None) or getattr(brand, "default_hex_color", None),
                "prominence": link.prominence_percent,
            })
        return sponsors

    def build_nodes(self, teams: List[TeamNode]) -> List[Dict]:
        nodes: List[Dict] = []
        for node in teams:
            node_dto = build_team_summary_dto(node)
            node_dto["eras"] = [build_timeline_era_dto(era) for era in node.eras]
            node_dto["eras"] = sorted(node_dto["eras"], key=lambda e: e["year"])
            nodes.append(node_dto)
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
        return links
