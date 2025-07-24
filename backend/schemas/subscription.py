from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"

class SubscriptionCreate(BaseModel):
    user_id: int
    plan_id: int
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE

class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    plan_id: int
    status: SubscriptionStatus
    started_at: datetime

class SubscriptionUpdate(BaseModel):
    status: Optional[SubscriptionStatus] = None

from .user import UserOut  # Adjust the import path as needed
from .subscription_plan import SubscriptionPlanOut  # Adjust the import path as needed

# For relationships
class SubscriptionOutWithRelations(SubscriptionOut):
    user: UserOut
    plan: SubscriptionPlanOut
