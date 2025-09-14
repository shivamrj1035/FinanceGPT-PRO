"""
User model
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)  # USR001 format
    email = Column(String, unique=True, index=True)
    name = Column(String)
    phone = Column(String)
    password_hash = Column(String)

    # Profile
    age = Column(Integer)
    occupation = Column(String)
    monthly_income = Column(Float, default=0)
    risk_tolerance = Column(String, default="MODERATE")  # LOW, MODERATE, HIGH

    # Credit info
    credit_score = Column(Integer, default=750)
    pan_number = Column(String)
    aadhar_number = Column(String)

    # Preferences
    preferred_language = Column(String, default="en")
    notification_enabled = Column(Boolean, default=True)
    two_factor_enabled = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)

    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"