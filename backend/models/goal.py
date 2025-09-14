"""
Financial Goal model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(String, unique=True, index=True)  # GOAL001 format
    user_id = Column(String, ForeignKey("users.user_id"))

    # Goal details
    name = Column(String)
    description = Column(Text, nullable=True)
    category = Column(String)  # EMERGENCY, VACATION, EDUCATION, RETIREMENT, etc.
    priority = Column(String, default="MEDIUM")  # LOW, MEDIUM, HIGH, EMERGENCY

    # Financial details
    target_amount = Column(Float)
    current_amount = Column(Float, default=0)
    monthly_contribution = Column(Float, default=0)
    currency = Column(String, default="INR")

    # Timeline
    target_date = Column(DateTime)
    start_date = Column(DateTime, default=datetime.utcnow)

    # Progress tracking
    progress_percentage = Column(Float, default=0)
    status = Column(String, default="ACTIVE")  # ACTIVE, ON_TRACK, BEHIND, ACHIEVED, PAUSED

    # AI recommendations
    recommended_monthly = Column(Float, nullable=True)
    achievability_score = Column(Float, nullable=True)
    ai_suggestions = Column(Text, nullable=True)

    # Notifications
    reminder_enabled = Column(Boolean, default=True)
    reminder_frequency = Column(String, default="MONTHLY")  # WEEKLY, MONTHLY

    # Status
    is_active = Column(Boolean, default=True)
    is_flexible = Column(Boolean, default=True)  # Can adjust target date

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    achieved_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="goals")

    def __repr__(self):
        return f"<Goal {self.name} - {self.progress_percentage}%>"