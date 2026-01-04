from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.core.database import Base
from api.modules.auth.models import generate_uuid

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    message = Column(Text, nullable=False)
    payload = Column(JSON, nullable=True) # Stored as JSON
    is_read = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("api.modules.auth.models.User", backref="notifications")
