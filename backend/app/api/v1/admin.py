from fastapi import APIRouter
from app.services.timeline_service import TimelineService

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

@router.post("/cache/invalidate")
def invalidate_cache():
    """Invalidate the timeline cache. Admin/ops utility.

    In setups without auth, treat this as a no-op risk; in production,
    guard with proper authentication/authorization.
    """
    TimelineService.invalidate_cache()
    return {"status": "ok", "message": "timeline cache invalidated"}
