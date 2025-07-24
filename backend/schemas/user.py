from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

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
    email: EmailStr
    role: UserRole
    created_at: datetime
    updated_at: datetime

class UserOutWithRelations(UserOut):
    contents: List['ContentOut'] = []
    agency_reports: List['ReportOut'] = []
    subscriptions: List['SubscriptionOut'] = []
    agency_reports: List['ReportOut'] = []
    subscriptions: List['SubscriptionOut'] = []
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
