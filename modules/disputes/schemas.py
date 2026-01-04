from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from api.shared.enums import DisputeStatus

class DisputeCreate(BaseModel):
    job_id: str
    reason: str

class DisputeResolve(BaseModel):
    outcome: DisputeStatus # RESOLVED or REJECTED
    notes: str

class DisputeResponse(DisputeCreate):
    id: str
    created_by_id: str
    status: DisputeStatus
    resolution_notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
