from .base import BaseSchema, TimestampMixin, IDMixin, PaginationParams, PaginatedResponse

# Import specific schemas
from .user import UserCreate, UserOut, UserOutWithRelations
from .content import ContentCreate, ContentOut, ContentOutWithCreator, ContentOutWithReports, ContentOutFull
from .report import ReportCreate, ReportOut, ReportOutWithRelations
from .subscription_plan import SubscriptionPlanCreate, SubscriptionPlanOut, SubscriptionPlanOutWithSubscriptions
from .subscription import SubscriptionCreate, SubscriptionOut, SubscriptionOutWithRelations

# Update forward references for relationships
UserOutWithRelations.model_rebuild()
ContentOutWithCreator.model_rebuild()
ContentOutWithReports.model_rebuild()
ContentOutFull.model_rebuild()
ReportOutWithRelations.model_rebuild()
SubscriptionPlanOutWithSubscriptions.model_rebuild()
SubscriptionOutWithRelations.model_rebuild()

__all__ = [
    "BaseSchema",
    "TimestampMixin",
    "IDMixin",
    "PaginationParams",
    "PaginatedResponse",
    # User schemas
    "UserCreate", "UserOut", "UserOutWithRelations",
    # Content schemas
    "ContentCreate", "ContentOut", "ContentOutWithCreator",
    "ContentOutWithReports", "ContentOutFull",
    # Report schemas
    "ReportCreate", "ReportOut", "ReportOutWithRelations",
    # SubscriptionPlan schemas
    "SubscriptionPlanCreate", "SubscriptionPlanOut",
    "SubscriptionPlanOutWithSubscriptions",
    # Subscription schemas
    "SubscriptionCreate", "SubscriptionOut",
    "SubscriptionOutWithRelations",
]
