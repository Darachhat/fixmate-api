from sqlalchemy import Column, String, Boolean, Float
from api.core.database import Base
from api.modules.auth.models import generate_uuid

class Service(Base):
    __tablename__ = "services"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    base_price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True) # Soft delete
