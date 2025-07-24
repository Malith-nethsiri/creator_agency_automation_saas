from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    agency_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    agency = relationship("User", back_populates="agency_reports")
    content = relationship("Content", back_populates="reports")
