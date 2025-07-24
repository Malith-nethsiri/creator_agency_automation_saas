from fastapi import APIRouter
from .auth_routes import router as auth_router
from .content_routes import router as content_router
from .report_routes import router as report_router
from .subscription_routes import router as subscription_router
from .test_email_routes import router as test_email_router
from .health_routes import router as health_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(content_router, prefix="/content", tags=["Content"])
api_router.include_router(report_router, prefix="/reports", tags=["Reports"])
api_router.include_router(subscription_router, prefix="/subscriptions", tags=["Subscriptions"])
api_router.include_router(test_email_router, prefix="/test", tags=["Test Email"])
