from pydantic import BaseModel
from typing import List, Optional

from .user import UserOut
from .content import ContentOut


class UserWithRelations(UserOut):
    contents: Optional[List[ContentOut]] = []


class ContentWithUser(ContentOut):
    user: Optional[UserOut]
