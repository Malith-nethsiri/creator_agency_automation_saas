from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from models.base import Base

class UserRole(enum.Enum):
    CREATOR = "creator"
    AGENCY = "agency"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contents = relationship("Content", back_populates="creator")
    agency_reports = relationship("Report", back_populates="agency")
    subscriptions = relationship("Subscription", back_populates="user")
