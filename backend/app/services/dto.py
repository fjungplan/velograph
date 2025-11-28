from __future__ import annotations

from typing import Dict, Any
from app.models.team import TeamEra, TeamNode


def build_timeline_era_dto(era: TeamEra) -> Dict[str, Any]:
    sponsors = []
    for link in getattr(era, "sponsor_links", []) or []:
        brand = getattr(link, "brand", None)
        sponsors.append(
            {
                "brand": brand.brand_name if brand else None,
                "color": brand.default_hex_color if brand else None,
                "prominence": link.prominence_percent,
            }
        )
    return {
        "year": era.season_year,
        "name": era.registered_name,
        "tier": era.tier_level,
        "sponsors": sponsors,
    }


def build_team_summary_dto(node: TeamNode) -> Dict[str, Any]:
    return {
        "id": str(node.node_id),
        "founding_year": node.founding_year,
        "dissolution_year": node.dissolution_year,
    }