from fastapi import APIRouter
from .auth_routes import router as auth_router
from .content_routes import router as content_router
from .report_routes import router as report_router
from .subscription_routes import router as subscription_router
from .test_email_routes import router as test_email_router  # ✅ Added this

api_router = APIRouter()

# ✅ Existing routes
api_router.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
api_router.include_router(content_router, prefix="/api/v1/content", tags=["Content"])
api_router.include_router(report_router, prefix="/api/v1/reports", tags=["Reports"])
api_router.include_router(subscription_router, prefix="/api/v1/subscriptions", tags=["Subscriptions"])

# ✅ Test email route
api_router.include_router(test_email_router, prefix="/api/v1/test", tags=["Test Email"])
