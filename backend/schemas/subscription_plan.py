from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class SubscriptionPlanCreate(BaseModel):
    name: str
    price: Decimal
    features: Optional[str] = None

class SubscriptionPlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal
    features: Optional[str] = None
    created_at: datetime

from .subscription import SubscriptionOut  # Adjust the import path as needed

class SubscriptionPlanOutWithSubscriptions(SubscriptionPlanOut):
    subscriptions: List[SubscriptionOut] = []
