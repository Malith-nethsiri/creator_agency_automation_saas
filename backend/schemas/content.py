from pydantic import BaseModel
from typing import Optional

class ContentBase(BaseModel):
    title: str
    description: Optional[str] = None


class ContentOut(ContentBase):
    id: int

    class Config:
        from_attributes = True
