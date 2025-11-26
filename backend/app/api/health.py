"""
Health check endpoint for monitoring application and database status.
"""
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from datetime import datetime
from app.db.database import check_db_connection

router = APIRouter()


@router.get("/health")
async def health_check():
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
    
    # Check database connectivity - catch any exceptions
    try:
        db_connected = await check_db_connection()
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
