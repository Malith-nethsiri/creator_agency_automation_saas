from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from core.config import settings
from core.utils import APIException, create_response
from routes.api import api_router
from database import engine
from models import Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A comprehensive SaaS platform for creator agency automation",
    version=settings.VERSION,
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """Handle custom API exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_response(
            success=False,
            message=exc.detail,
        )
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_response(
            success=False,
            message=exc.detail,
        )
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=422,
        content=create_response(
            success=False,
            message="Validation error",
            data={"errors": exc.errors()}
        )
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors"""
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=create_response(
            success=False,
            message="Database error occurred",
        )
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=create_response(
            success=False,
            message="Internal server error",
        )
    )

# Include API router with all routes
app.include_router(api_router, prefix="/api/v1")

# Event handlers
@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} is starting up...")
    logger.info(f"📊 Debug mode: {settings.DEBUG}")
    logger.info(f"🔗 Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    logger.info("✅ All routes loaded:")
    logger.info("   - /api/v1/health - Health check endpoints")
    logger.info("   - /api/v1/auth - Authentication endpoints")
    logger.info("   - /api/v1/content - Content management endpoints")
    logger.info("   - /api/v1/reports - Report management endpoints")
    logger.info("   - /api/v1/subscriptions - Subscription management endpoints")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info(f"🛑 {settings.PROJECT_NAME} is shutting down...")
