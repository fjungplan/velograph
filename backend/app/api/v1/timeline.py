from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.timeline import TimelineResponse
from app.services.timeline_service import TimelineService
from app.core.etag import compute_etag

router = APIRouter(prefix="/api/v1", tags=["timeline"])


@router.get("/timeline", response_model=TimelineResponse)
async def get_timeline(
    request: Request,
    response: Response,
    start_year: int = Query(1900, ge=1900, le=2100),
    end_year: int = Query(datetime.utcnow().year, ge=1900, le=2100),
    include_dissolved: bool = True,
    tier_filter: Optional[List[int]] = Query(None),
    session: AsyncSession = Depends(get_db),
):
    service = TimelineService(session)
    data = await service.get_graph_data(
        start_year=start_year,
        end_year=end_year,
        include_dissolved=include_dissolved,
        tier_filter=tier_filter,
    )
    body = jsonable_encoder(data)
    etag = compute_etag(body)
    inm = request.headers.get("if-none-match")
    if inm == etag:
        resp = Response(status_code=304)
        resp.headers["ETag"] = etag
        resp.headers["Cache-Control"] = "max-age=300"
        return resp
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "max-age=300"
    return data
