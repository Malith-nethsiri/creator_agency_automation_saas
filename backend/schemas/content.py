from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from .user import UserOut  # Adjust the import path as needed

class ContentBase(BaseModel):
    title: str
    description: Optional[str] = None
    description: Optional[str] = None


class ContentOut(ContentBase):
    id: int
    user: Optional["UserOut"]  # Forward reference to avoid circular import

    class Config:
        from_attributes = True

from pydantic import BaseModel

ContentOut.model_rebuild()
