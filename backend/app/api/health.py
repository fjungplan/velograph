"""
Health check endpoint for monitoring application and database status.
"""
from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Callable, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.database import get_db

router = APIRouter()


async def check_db_connection(session: AsyncSession) -> bool:
    """Helper that runs a trivial query; kept for test patching."""
    try:
        await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_checker() -> Callable[[AsyncSession], Awaitable[bool]]:
    """Dependency provider for the DB connectivity check function."""
    return check_db_connection


@router.get("/health")
async def health_check(
    session: AsyncSession = Depends(get_db),
    checker: Callable[[AsyncSession], Awaitable[bool]] = Depends(get_checker),
):
    """
    Health check endpoint that verifies application and database status.
    
    Returns:
        200 OK if healthy with database connected
        503 Service Unavailable if database is not available
        
    Response format:
        {
            "status": "healthy" | "unhealthy",
            "database": "connected" | "disconnected",
            "timestamp": "ISO8601 timestamp"
        }
    """
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Check database connectivity against the injected session (overridable in tests)
    try:
        db_connected = await checker(session)
    except Exception:
        db_connected = False
    
    if db_connected:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "database": "connected",
                "timestamp": timestamp,
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "timestamp": timestamp,
                "detail": "Database connection failed"
            }
        )
