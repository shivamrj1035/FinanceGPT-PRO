"""
Investment model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base

class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    investment_id = Column(String, unique=True, index=True)  # INV001 format
    user_id = Column(String, ForeignKey("users.user_id"))

    # Investment details
    name = Column(String)
    type = Column(String)  # MUTUAL_FUND, STOCK, FD, PPF, NPS, GOLD, CRYPTO
    category = Column(String)  # EQUITY, DEBT, HYBRID, COMMODITY
    subcategory = Column(String, nullable=True)  # LARGE_CAP, MID_CAP, etc.

    # Provider info
    provider = Column(String)  # AMC name, Bank name, etc.
    scheme_code = Column(String, nullable=True)
    folio_number = Column(String, nullable=True)

    # Financial details
    invested_amount = Column(Float)
    current_value = Column(Float)
    units = Column(Float, nullable=True)
    nav = Column(Float, nullable=True)  # Net Asset Value
    currency = Column(String, default="INR")

    # Returns
    returns_amount = Column(Float, default=0)
    returns_percentage = Column(Float, default=0)
    xirr = Column(Float, nullable=True)  # Extended Internal Rate of Return
    cagr = Column(Float, nullable=True)  # Compound Annual Growth Rate

    # SIP details (if applicable)
    is_sip = Column(Boolean, default=False)
    sip_amount = Column(Float, nullable=True)
    sip_date = Column(Integer, nullable=True)  # Day of month
    sip_frequency = Column(String, nullable=True)  # MONTHLY, QUARTERLY

    # Risk profile
    risk_level = Column(String, default="MODERATE")  # LOW, MODERATE, HIGH, VERY_HIGH
    expense_ratio = Column(Float, nullable=True)
    exit_load = Column(Float, nullable=True)

    # Tax details
    tax_category = Column(String, nullable=True)  # ELSS, NON_ELSS
    lock_in_period = Column(Integer, nullable=True)  # In months

    # Goal linking
    linked_goal_id = Column(String, nullable=True)

    # Status
    status = Column(String, default="ACTIVE")  # ACTIVE, MATURED, REDEEMED, PAUSED
    is_active = Column(Boolean, default=True)

    # Timestamps
    purchase_date = Column(DateTime)
    maturity_date = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="investments")

    def __repr__(self):
        return f"<Investment {self.name} - {self.returns_percentage}%>"