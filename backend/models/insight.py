"""
AI-generated Insight model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base

class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    insight_id = Column(String, unique=True, index=True)  # INSIGHT001 format
    user_id = Column(String, ForeignKey("users.user_id"))

    # Insight details
    type = Column(String)  # SPENDING, SAVING, INVESTMENT, GOAL, TAX, CREDIT
    category = Column(String)  # Specific category within type
    title = Column(String)
    description = Column(Text)

    # Recommendations
    recommendation = Column(Text)
    action_items = Column(JSON)  # List of action items
    priority = Column(String, default="MEDIUM")  # LOW, MEDIUM, HIGH

    # Financial impact
    potential_savings = Column(Float, nullable=True)
    potential_earnings = Column(Float, nullable=True)
    impact_timeframe = Column(String, nullable=True)  # IMMEDIATE, SHORT_TERM, LONG_TERM

    # AI metadata
    confidence_score = Column(Float, default=0.8)
    model_version = Column(String, default="gemini-1.5")
    analysis_data = Column(JSON, nullable=True)  # Raw analysis data

    # User interaction
    is_read = Column(Boolean, default=False)
    is_acted_upon = Column(Boolean, default=False)
    user_feedback = Column(String, nullable=True)  # HELPFUL, NOT_HELPFUL, NEUTRAL
    feedback_comment = Column(Text, nullable=True)

    # Related entities
    related_transactions = Column(JSON, nullable=True)  # List of transaction IDs
    related_goals = Column(JSON, nullable=True)  # List of goal IDs
    related_investments = Column(JSON, nullable=True)  # List of investment IDs

    # Validity
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)

    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    acted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="insights")

    def __repr__(self):
        return f"<Insight {self.type} - {self.title}>"