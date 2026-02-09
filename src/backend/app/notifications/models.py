from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from src.backend.app.common.models import Base

class NotificationType(str, enum.Enum):
    INFO = "info"
    SUCCESS = "success" 
    WARNING = "warning"
    ERROR = "error"
    ACTION_REQUIRED = "action_required"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default=NotificationType.INFO, nullable=False) # stored as string for flexibility
    
    link = Column(String(500), nullable=True) # Optional action link
    is_read = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", backref="notifications")
