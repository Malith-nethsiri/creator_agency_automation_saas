from .api import api_router
from .health import router as health_router

# TODO: Import specific routers when created
# from .auth import router as auth_router
# from .users import router as users_router
# from .content import router as content_router
# from .reports import router as reports_router
# from .subscriptions import router as subscriptions_router

__all__ = [
    "api_router",
    "health_router"
]
