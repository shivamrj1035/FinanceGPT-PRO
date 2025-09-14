"""
Bank Account model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, unique=True, index=True)  # ACC001 format
    user_id = Column(String, ForeignKey("users.user_id"))

    # Account details
    bank_name = Column(String)
    account_type = Column(String)  # SAVINGS, CURRENT, CREDIT_CARD, LOAN
    account_number = Column(String)  # Masked version ****1234
    ifsc_code = Column(String)

    # Balance info
    balance = Column(Float, default=0)
    available_balance = Column(Float, default=0)
    currency = Column(String, default="INR")

    # Credit card specific
    credit_limit = Column(Float, nullable=True)
    credit_used = Column(Float, nullable=True)
    minimum_due = Column(Float, nullable=True)
    due_date = Column(DateTime, nullable=True)

    # Loan specific
    loan_amount = Column(Float, nullable=True)
    emi_amount = Column(Float, nullable=True)
    interest_rate = Column(Float, nullable=True)
    tenure_months = Column(Integer, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Account {self.bank_name} - {self.account_type}>"