from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Import ReportOut, SubscriptionOut, and ContentOut if they are defined in other modules
from .content import ContentOut
from .report import ReportOut
from .subscription import SubscriptionOut

class UserRole(str, Enum):
    CREATOR = "creator"
    AGENCY = "agency"
    ADMIN = "admin"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
class UserOutWithRelations(UserOut):
    contents: List['ContentOut'] = []
    agency_reports: List['ReportOut'] = []
    subscriptions: List['SubscriptionOut'] = []
    contents: List['ContentOut'] = []
    agency_reports: List['ReportOut'] = []
class Token(BaseModel):
    access_token: str
    token_type: str

# If using forward references, update them after all classes are defined
UserOutWithRelations.update_forward_refs()
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
