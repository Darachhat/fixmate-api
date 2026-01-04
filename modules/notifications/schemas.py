from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class NotificationResponse(BaseModel):
    id: str
    message: str
    payload: Optional[Dict[str, Any]] = None
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
