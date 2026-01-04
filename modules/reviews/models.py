from sqlalchemy import Column, String, ForeignKey, Integer, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
from modules.auth.models import generate_uuid

class Review(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), unique=True, nullable=False)
    reviewer_id = Column(String, ForeignKey("users.id"), nullable=False)
    technician_id = Column(String, ForeignKey("technicians.id"), nullable=False)
    
    rating = Column(Integer, nullable=False) # 1-5
    comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    job = relationship("modules.jobs.models.Job", backref="review")
    technician = relationship("modules.users.models.Technician")
