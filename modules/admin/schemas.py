from pydantic import BaseModel
from datetime import datetime

class AuditLogResponse(BaseModel):
    id: str
    user_id: str
    action: str
    details: str
    created_at: datetime
    class Config:
        from_attributes = True
