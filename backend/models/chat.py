"""
Chat Session and Message models
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))

    # Session details
    title = Column(String, nullable=True)
    context = Column(JSON, nullable=True)  # Session context

    # AI settings for this session
    ai_model = Column(String, default="gemini-1.5-flash")
    temperature = Column(Float, default=0.7)
    prompt_type = Column(String, default="general")  # general, investment, tax, etc.

    # Statistics
    message_count = Column(Integer, default=0)
    tools_used = Column(JSON, nullable=True)  # List of tools used in session
    topics_discussed = Column(JSON, nullable=True)  # List of topics

    # Status
    is_active = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession {self.session_id}>"


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.session_id"))

    # Message details
    role = Column(String)  # user, assistant, system
    content = Column(Text)

    # For assistant messages
    suggestions = Column(JSON, nullable=True)  # Follow-up suggestions
    tools_used = Column(JSON, nullable=True)  # Tools used for this response
    data_referenced = Column(JSON, nullable=True)  # Data IDs referenced
    confidence_score = Column(Float, nullable=True)

    # For user messages
    intent = Column(String, nullable=True)  # Detected intent
    entities = Column(JSON, nullable=True)  # Extracted entities

    # Attachments (future feature)
    attachments = Column(JSON, nullable=True)

    # Feedback
    is_helpful = Column(Boolean, nullable=True)
    feedback_comment = Column(Text, nullable=True)

    # Status
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    edited_at = Column(DateTime, nullable=True)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage {self.role}: {self.content[:50]}...>"