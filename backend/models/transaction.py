"""
Transaction model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)  # TXN001 format
    account_id = Column(String, ForeignKey("accounts.account_id"))

    # Transaction details
    amount = Column(Float)
    transaction_type = Column(String)  # DEBIT, CREDIT
    category = Column(String)  # FOOD, TRANSPORT, SHOPPING, etc.
    subcategory = Column(String, nullable=True)

    # Merchant info
    merchant = Column(String)
    merchant_category = Column(String, nullable=True)
    location = Column(String, nullable=True)

    # Payment method
    payment_method = Column(String)  # UPI, CARD, NETBANKING, CASH
    reference_number = Column(String, nullable=True)

    # Additional info
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    tags = Column(String, nullable=True)  # Comma-separated tags

    # Fraud detection
    is_flagged = Column(Boolean, default=False)
    fraud_score = Column(Float, default=0)
    fraud_reason = Column(Text, nullable=True)

    # Recurring transaction
    is_recurring = Column(Boolean, default=False)
    recurring_id = Column(String, nullable=True)

    # Status
    status = Column(String, default="COMPLETED")  # PENDING, COMPLETED, FAILED
    is_hidden = Column(Boolean, default=False)

    # Timestamps
    transaction_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    account = relationship("Account", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.merchant} - {self.amount}>"