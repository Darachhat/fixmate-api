from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
from modules.auth.models import generate_uuid
from shared.enums import DisputeStatus

class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    created_by_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    reason = Column(Text, nullable=False)
    status = Column(SQLEnum(DisputeStatus), default=DisputeStatus.OPEN)
    resolution_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    job = relationship("modules.jobs.models.Job", backref="disputes")
    created_by = relationship("modules.auth.models.User")
