from pydantic import BaseModel, EmailStr
from typing import List, Optional


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True  # For SQLAlchemy ORM mode


from .content import ContentOut  # Make sure this import path is correct

class UserWithRelations(UserOut):
    contents: Optional[List[ContentOut]] = []  # Use imported ContentOut directly

from pydantic import BaseModel

UserWithRelations.model_rebuild()

