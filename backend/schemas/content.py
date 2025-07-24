from pydantic import BaseModel
from typing import Optional, List
from .user import UserOut  # Needed for creator relations

class ContentBase(BaseModel):
    title: str
    description: Optional[str] = None

class ContentCreate(ContentBase):
    pass

class ContentUpdate(ContentBase):
    title: Optional[str] = None
    description: Optional[str] = None

class ContentOut(ContentBase):
    id: int

    class Config:
        from_attributes = True

# ✅ Advanced schemas
class ContentOutWithCreator(ContentOut):
    creator: Optional[UserOut]

class ContentOutWithReports(ContentOut):
    reports: Optional[List[str]] = []  # Adjust type to match your DB model

class ContentOutFull(ContentOutWithCreator, ContentOutWithReports):
    pass
