from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.core.database import Base
from api.modules.auth.models import generate_uuid
from api.shared.enums import JobStatus, JobOfferStatus

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    customer_id = Column(String, ForeignKey("users.id"), nullable=False)
    technician_id = Column(String, ForeignKey("technicians.id"), nullable=True) # Initially null
    service_id = Column(String, ForeignKey("services.id"), nullable=False)
    
    status = Column(SQLEnum(JobStatus), default=JobStatus.REQUESTED, nullable=False)
    
    description = Column(String, nullable=True)
    location = Column(String, nullable=False) # Simplified for now
    
    # Pricing snapshot
    estimated_price = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("api.modules.auth.models.User", foreign_keys=[customer_id], backref="requested_jobs")
    technician = relationship("api.modules.users.models.Technician", backref="assigned_jobs")
    service = relationship("api.modules.services.models.Service")
    offers = relationship("JobOffer", back_populates="job")

class JobOffer(Base):
    __tablename__ = "job_offers"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    technician_id = Column(String, ForeignKey("technicians.id"), nullable=False)
    status = Column(SQLEnum(JobOfferStatus), default=JobOfferStatus.PENDING, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    job = relationship("Job", back_populates="offers")
    technician = relationship("api.modules.users.models.Technician")
