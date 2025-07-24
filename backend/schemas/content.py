from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime
from .user import UserOut  # Import UserOut from the appropriate module
from .report import ReportOut  # Import ReportOut from the appropriate module

class ContentCreate(BaseModel):
    title: str
    file_url: str
    creator_id: int

class ContentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    file_url: str
    creator_id: int
    created_at: datetime

class ContentOutWithCreator(ContentOut):
    creator: 'UserOut'

class ContentOutWithReports(ContentOut):
    reports: List['ReportOut'] = []

class ContentOutFull(ContentOut):
    creator: 'UserOut'
    reports: List['ReportOut'] = []
class ContentOutWithReports(ContentOut):
    reports: List['ReportOut'] = []

class ContentOutFull(ContentOut):
    creator: 'UserOut'
    reports: List['ReportOut'] = []
