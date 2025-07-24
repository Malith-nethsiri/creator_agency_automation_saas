from pydantic import BaseModel
from typing import Optional

class ContentBase(BaseModel):
    title: str
    description: Optional[str] = None


class ContentOut(ContentBase):
    id: int
    user: Optional["UserOut"]  # Forward reference to avoid circular import

    class Config:
        from_attributes = True

from pydantic import BaseModel

ContentOut.model_rebuild()
