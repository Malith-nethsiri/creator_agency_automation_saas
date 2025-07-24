from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    features = Column(Text)  # JSON string or comma-separated features
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")
