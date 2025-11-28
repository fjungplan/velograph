from typing import List, Dict
from app.models.team import TeamNode, TeamEra
from app.models.lineage import LineageEvent


class GraphBuilder:
    def build_jersey_composition(self, era: TeamEra) -> List[Dict]:
        sponsors = []
        for link in era.sponsors_ordered:
            sponsors.append({
                "brand": link.brand.brand_name,
                "color": link.brand.color_hex,
                "prominence": link.prominence_percent,
            })
        return sponsors

    def build_nodes(self, teams: List[TeamNode]) -> List[Dict]:
        nodes: List[Dict] = []
        for node in teams:
            eras = []
            for era in node.eras:
                eras.append({
                    "year": era.season_year,
                    "name": era.registered_name,
                    "tier": era.tier_level,
                    "sponsors": self.build_jersey_composition(era),
                })
            nodes.append({
                "id": str(node.node_id),
                "founding_year": node.founding_year,
                "dissolution_year": node.dissolution_year,
                "eras": sorted(eras, key=lambda e: e["year"]),
            })
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
