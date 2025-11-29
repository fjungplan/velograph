"""Admin API endpoints for cache management and scraper control."""
from typing import Dict
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel

from app.services.timeline_service import TimelineService
from app.scraper import create_scheduler


router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

# Global scheduler instance
_scheduler = None


class ScraperStartRequest(BaseModel):
    """Request body for starting the scraper."""
    interval: int = 300  # Default 5 minutes


class ScraperTriggerRequest(BaseModel):
    """Request body for manually triggering a scrape."""
    team_identifier: str


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


class ScraperResultResponse(BaseModel):
    """Response with scraper results."""
    results: Dict[str, Dict]


@router.post("/cache/invalidate")
def invalidate_cache():
    """Invalidate the timeline cache. Admin/ops utility.

    In setups without auth, treat this as a no-op risk; in production,
    guard with proper authentication/authorization.
    """
    TimelineService.invalidate_cache()
    return {"status": "ok", "message": "timeline cache invalidated"}


@router.post(
    "/scraper/start",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK
)
async def start_scraper(
    request: ScraperStartRequest,
    background_tasks: BackgroundTasks
) -> MessageResponse:
    """
    Start the scraper scheduler in continuous mode.
    
    Args:
        request: Configuration for scraper interval
        background_tasks: FastAPI background tasks
    
    Returns:
        Success message
    
    Raises:
        HTTPException: If scraper is already running
    """
    global _scheduler
    
    if _scheduler is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scraper is already running"
        )
    
    _scheduler = create_scheduler()
    
    # Start in background (note: in production, use proper task queue)
    async def run_scheduler():
        try:
            await _scheduler.run_continuous(
                team_identifier="default",  # Placeholder
                interval=request.interval
            )
        except Exception as e:
            print(f"Scheduler error: {e}")
    
    background_tasks.add_task(run_scheduler)
    
    return MessageResponse(message="Scraper started successfully")


@router.post(
    "/scraper/stop",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK
)
async def stop_scraper() -> MessageResponse:
    """
    Stop the scraper scheduler.
    
    Returns:
        Success message
    
    Raises:
        HTTPException: If scraper is not running
    """
    global _scheduler
    
    if _scheduler is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scraper is not running"
        )
    
    _scheduler.stop()
    await _scheduler.close()
    _scheduler = None
    
    return MessageResponse(message="Scraper stopped successfully")


@router.post(
    "/scraper/trigger",
    response_model=ScraperResultResponse,
    status_code=status.HTTP_200_OK
)
async def trigger_scraper(request: ScraperTriggerRequest) -> ScraperResultResponse:
    """
    Manually trigger a one-time scrape for a specific team.
    
    Args:
        request: Team identifier to scrape
    
    Returns:
        Results from all scrapers
    """
    scheduler = create_scheduler()
    try:
        results = await scheduler.run_once(request.team_identifier)
        return ScraperResultResponse(results=results)
    finally:
        await scheduler.close()
