from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ReportCreate(BaseModel):
    name: str
    agency_id: int
    content_id: int

class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    agency_id: int
    content_id: int
    created_at: datetime

class ReportOutWithRelations(ReportOut):
    agency: 'UserOut'
    content: 'ContentOut'
