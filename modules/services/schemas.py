from pydantic import BaseModel
from typing import Optional

class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    base_price: float

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None

class ServiceResponse(ServiceBase):
    id: str
    is_active: bool

    class Config:
        from_attributes = True
