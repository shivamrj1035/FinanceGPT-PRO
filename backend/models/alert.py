"""
Alert/Notification model
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, unique=True, index=True)  # ALERT001 format
    user_id = Column(String, ForeignKey("users.user_id"))

    # Alert details
    type = Column(String)  # FRAUD, GOAL, BILL, INVESTMENT, INSIGHT, SYSTEM
    title = Column(String)
    message = Column(Text)
    severity = Column(String, default="INFO")  # INFO, LOW, MEDIUM, HIGH, CRITICAL

    # Related entities
    related_entity_type = Column(String, nullable=True)  # transaction, goal, investment
    related_entity_id = Column(String, nullable=True)

    # Action required
    action_required = Column(Boolean, default=False)
    action_type = Column(String, nullable=True)  # VERIFY, APPROVE, REVIEW
    action_deadline = Column(DateTime, nullable=True)
    action_taken = Column(String, nullable=True)

    # Delivery status
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)

    # Notification channels
    email_sent = Column(Boolean, default=False)
    sms_sent = Column(Boolean, default=False)
    push_sent = Column(Boolean, default=False)
    in_app_shown = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    dismissed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="alerts")

    def __repr__(self):
        return f"<Alert {self.type} - {self.title}>"