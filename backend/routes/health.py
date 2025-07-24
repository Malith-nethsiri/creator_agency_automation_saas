from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from core.utils import create_response
from core.config import settings

router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint"""
    return create_response(
        success=True,
        message=f"{settings.PROJECT_NAME} API is running",
        data={"version": settings.VERSION}
    )

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connection test"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return create_response(
            success=True,
            message="Service is healthy",
            data={
                "database": "connected",
                "version": settings.VERSION,
                "debug": settings.DEBUG
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=create_response(
                success=False,
                message="Service is unhealthy",
                data={"database": "disconnected", "error": str(e)}
            )
        )

@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong"}
