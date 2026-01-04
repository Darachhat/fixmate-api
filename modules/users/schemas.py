from pydantic import BaseModel
from typing import Optional, List

class TechnicianBase(BaseModel):
    bio: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class TechnicianCreate(TechnicianBase):
    pass

class TechnicianUpdate(TechnicianBase):
    pass

class TechnicianDocumentBase(BaseModel):
    file_url: str
    document_type: str

class TechnicianDocumentResponse(TechnicianDocumentBase):
    id: str
    class Config:
        from_attributes = True

class TechnicianResponse(TechnicianBase):
    id: str
    user_id: str
    is_verified: bool
    average_rating: float
    documents: List[TechnicianDocumentResponse] = []

    class Config:
        from_attributes = True
