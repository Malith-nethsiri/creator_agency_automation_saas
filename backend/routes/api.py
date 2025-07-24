from fastapi import APIRouter
from .health import router as health_router
from .auth_routes import router as auth_router
from .content_routes import router as content_router
from .report_routes import router as report_router
from .subscription_routes import router as subscription_router
from .payment_routes import router as payment_router
from .test_email_routes import router as test_email_router

api_router = APIRouter()

api_router.include_router(test_email_router, prefix="/api/v1/test", tags=["Test"])

# Include all routers
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(content_router, prefix="/content", tags=["content"])
api_router.include_router(report_router, prefix="/reports", tags=["reports"])
api_router.include_router(subscription_router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(payment_router, prefix="/payments", tags=["payments"])
