from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from api.core.database import Base
from api.modules.auth.models import generate_uuid

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
