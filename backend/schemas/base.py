from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    class Config:
        orm_mode = True
        from_attributes = True

class TimestampMixin(BaseModel):
    """Mixin for models with timestamps"""
    created_at: datetime
    updated_at: datetime

class IDMixin(BaseModel):
    """Mixin for models with ID"""
    id: int

class PaginationParams(BaseModel):
    """Schema for pagination parameters"""
    page: int = 1
    per_page: int = 10

    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "per_page": 10
            }
        }

class PaginatedResponse(BaseModel):
    """Schema for paginated responses"""
    items: list
    total: int
    page: int
    per_page: int
    pages: int
