from __future__ import annotations

from typing import Optional
from uuid import UUID
import hashlib

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.team_service import TeamService
from app.core.etag import compute_etag
from app.schemas.team import (
    TeamNodeWithEras,
    TeamNodeResponse,
    TeamEraResponse,
    TeamListResponse,
)
from app.schemas.team_detail import TeamHistoryResponse
from app.services.team_detail_service import TeamDetailService
from app.core.exceptions import NodeNotFoundException


router = APIRouter(prefix="/api/v1/teams", tags=["teams"])


@router.get("/{node_id}", response_model=TeamNodeWithEras)
async def get_team(
    node_id: UUID,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Return a single TeamNode with its eras.

    Eager-loads related eras (and lineage events for future use).
    """
    node = await TeamService.get_node_with_eras(db, node_id)
    if not node:
        raise NodeNotFoundException(f"TeamNode {node_id} not found")
    # Conditional ETag handling
    body = jsonable_encoder(node)
    etag = compute_etag(body)
    inm = request.headers.get("if-none-match") if request else None
    if inm == etag:
        resp = Response(status_code=304)
        resp.headers["ETag"] = etag
        resp.headers["Cache-Control"] = "max-age=300"
        return resp
    if response:
        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = "max-age=300"
    return node


@router.get("/{node_id}/history", response_model=TeamHistoryResponse)
async def get_team_history(node_id: UUID, request: Request, db: AsyncSession = Depends(get_db)):
    """Mobile-optimized chronological history for a team node with ETag support."""
    history = await TeamDetailService.get_team_history(db, str(node_id))
    if not history:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Compute ETag for conditional requests
    payload = history.model_dump_json()
    etag = hashlib.md5(payload.encode("utf-8")).hexdigest()
    
    # If-None-Match handling: return 304 if client's ETag matches
    inm = request.headers.get("If-None-Match")
    if inm and inm.strip() == etag:
        response = Response(status_code=304)
        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = "max-age=300"
        return response
    
    # Return full response with caching headers
    response = Response(content=payload, media_type="application/json")
    response.headers["Cache-Control"] = "max-age=300"
    response.headers["ETag"] = etag
    return response


@router.get("/{node_id}/eras", response_model=list[TeamEraResponse])
async def get_team_eras(
    node_id: UUID,
    request: Request,
    response: Response,
    year: Optional[int] = Query(default=None, ge=1900, le=2100),
    db: AsyncSession = Depends(get_db),
):
    """Return all TeamEra records for a given team node.

    Optional `year` filters to a specific season; results ordered by season_year DESC.
    """
    # Ensure node exists for 404 semantics
    node = await TeamService.get_node_with_eras(db, node_id)
    if not node:
        raise NodeNotFoundException(f"TeamNode {node_id} not found")
    eras = await TeamService.get_node_eras(db, node_id, year_filter=year)
    body = jsonable_encoder(eras)
    etag = compute_etag(body)
    inm = request.headers.get("if-none-match") if request else None
    if inm == etag:
        resp = Response(status_code=304)
        resp.headers["ETag"] = etag
        resp.headers["Cache-Control"] = "max-age=300"
        return resp
    if response:
        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = "max-age=300"
    return eras


@router.get("", response_model=TeamListResponse)
async def list_teams(
    request: Request,
    response: Response,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    active_in_year: Optional[int] = Query(default=None, ge=1900, le=2100),
    tier_level: Optional[int] = Query(default=None, ge=1, le=3),
    db: AsyncSession = Depends(get_db),
):
    """List teams with pagination and optional filters.

    - active_in_year: only teams with an era in that year
    - tier_level: only teams having any era with the given tier
    """
    nodes, total = await TeamService.list_nodes(
        db,
        skip=skip,
        limit=limit,
        active_in_year=active_in_year,
        tier_level=tier_level,
    )
    payload = {
        "items": nodes,
        "total": total,
        "skip": skip,
        "limit": limit,
    }
    body = jsonable_encoder(payload)
    etag = compute_etag(body)
    inm = request.headers.get("if-none-match") if request else None
    if inm == etag:
        resp = Response(status_code=304)
        resp.headers["ETag"] = etag
        resp.headers["Cache-Control"] = "max-age=300"
        return resp
    if response:
        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = "max-age=300"
    return payload
