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

# For relationships
class SubscriptionOutWithRelations(SubscriptionOut):
    user: 'UserOut'
    plan: 'SubscriptionPlanOut'
