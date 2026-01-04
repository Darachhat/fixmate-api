from sqlalchemy import Column, String, ForeignKey, Float, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
from modules.auth.models import generate_uuid
from shared.enums import PaymentStatus

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), unique=True, nullable=False)
    
    amount = Column(Float, nullable=False)
    platform_fee = Column(Float, nullable=False)
    technician_earnings = Column(Float, nullable=False) # Stored explicitly
    
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    job = relationship("modules.jobs.models.Job", backref="payment")
