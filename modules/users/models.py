from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship
from api.core.database import Base
from api.modules.auth.models import generate_uuid

# Technician Profile
class Technician(Base):
    __tablename__ = "technicians"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    bio = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    
    # Rating/Reputation from Step 11
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)

    user = relationship("api.modules.auth.models.User", backref="technician_profile")
    documents = relationship("TechnicianDocument", back_populates="technician")

class TechnicianDocument(Base):
    __tablename__ = "technician_documents"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    technician_id = Column(String, ForeignKey("technicians.id"), nullable=False)
    file_url = Column(String, nullable=False)
    document_type = Column(String, nullable=False) # e.g. ID, CERTIFICATE

    technician = relationship("Technician", back_populates="documents")
