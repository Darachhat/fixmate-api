from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewCreate(BaseModel):
    job_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ReviewResponse(ReviewCreate):
    id: str
    reviewer_id: str
    technician_id: str
    created_at: datetime

    class Config:
        from_attributes = True
