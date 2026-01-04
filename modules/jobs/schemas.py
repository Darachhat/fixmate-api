from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from api.shared.enums import JobStatus

class JobBase(BaseModel):
    service_id: str
    description: Optional[str] = None
    location: str

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: str
    customer_id: str
    technician_id: Optional[str] = None
    status: JobStatus
    created_at: datetime
    
    class Config:
        from_attributes = True
