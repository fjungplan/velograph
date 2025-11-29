from __future__ import annotations

from typing import Dict, Any, Optional
from app.models.team import TeamEra, TeamNode


def build_timeline_era_dto(era: TeamEra) -> Dict[str, Any]:
    sponsors = []
    for link in getattr(era, "sponsor_links", []) or []:
        brand = getattr(link, "brand", None)
        sponsors.append(
            {
                "brandId": str(getattr(brand, "brand_id", "")) if brand else None,
                "name": getattr(brand, "brand_name", None) if brand else None,
                "color": getattr(brand, "default_hex_color", None) if brand else None,
                "prominence": getattr(link, "prominence_percent", None),
                "rank": getattr(link, "rank_order", None),
            }
        )
    return {
        "eraId": str(getattr(era, "era_id", "")),
        "nodeId": str(getattr(era, "node_id", "")),
        "year": era.season_year,
        "name": era.registered_name,
        "tier": era.tier_level,
        "sponsors": sponsors,
    }


def build_team_summary_dto(node: TeamNode) -> Dict[str, Any]:
    # Determine the most recent era (by season_year) for display fields
    eras = getattr(node, "eras", []) or []
    latest: Optional[TeamEra] = None
    if eras:
        latest = max(eras, key=lambda e: (e.season_year or 0))
    return {
        "nodeId": str(node.node_id),
        "foundingYear": node.founding_year,
        "currentName": latest.registered_name if latest else None,
        "currentTier": latest.tier_level if latest else None,
    }