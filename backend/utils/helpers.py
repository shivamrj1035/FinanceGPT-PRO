"""
Helper utilities
"""

from datetime import datetime, date
from typing import Tuple
import random
import string

def generate_id(prefix: str, length: int = 6) -> str:
    """
    Generate unique ID with prefix
    """
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}{suffix}"

def calculate_age(birth_date: date) -> int:
    """
    Calculate age from birth date
    """
    today = date.today()
    age = today.year - birth_date.year

    # Check if birthday has occurred this year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age

def get_financial_year(date_obj: Optional[datetime] = None) -> Tuple[int, int]:
    """
    Get Indian financial year (April to March)
    """
    if not date_obj:
        date_obj = datetime.now()

    year = date_obj.year
    month = date_obj.month

    if month < 4:  # January to March
        start_year = year - 1
        end_year = year
    else:  # April to December
        start_year = year
        end_year = year + 1

    return start_year, end_year

def calculate_emi(principal: float, rate: float, tenure_months: int) -> float:
    """
    Calculate EMI for loan
    """
    if rate == 0:
        return principal / tenure_months

    monthly_rate = rate / 100 / 12
    emi = principal * monthly_rate * (1 + monthly_rate) ** tenure_months
    emi = emi / ((1 + monthly_rate) ** tenure_months - 1)

    return round(emi, 2)

def calculate_compound_interest(
    principal: float,
    rate: float,
    time_years: float,
    frequency: int = 1
) -> float:
    """
    Calculate compound interest
    frequency: 1=yearly, 2=half-yearly, 4=quarterly, 12=monthly
    """
    amount = principal * (1 + (rate / 100) / frequency) ** (frequency * time_years)
    return round(amount - principal, 2)

def calculate_sip_returns(
    monthly_amount: float,
    rate: float,
    months: int
) -> Tuple[float, float]:
    """
    Calculate SIP returns
    Returns: (maturity_amount, total_invested)
    """
    monthly_rate = rate / 100 / 12
    total_invested = monthly_amount * months

    if monthly_rate == 0:
        maturity_amount = total_invested
    else:
        maturity_amount = monthly_amount * (
            ((1 + monthly_rate) ** months - 1) / monthly_rate
        ) * (1 + monthly_rate)

    return round(maturity_amount, 2), total_invested

def calculate_tax_old_regime(income: float) -> float:
    """
    Calculate tax under old Indian tax regime
    """
    tax = 0

    if income <= 250000:
        tax = 0
    elif income <= 500000:
        tax = (income - 250000) * 0.05
    elif income <= 1000000:
        tax = 12500 + (income - 500000) * 0.20
    else:
        tax = 112500 + (income - 1000000) * 0.30

    # Add cess
    tax = tax * 1.04  # 4% health and education cess

    return round(tax, 2)

def calculate_tax_new_regime(income: float) -> float:
    """
    Calculate tax under new Indian tax regime (2023-24)
    """
    tax = 0

    if income <= 300000:
        tax = 0
    elif income <= 600000:
        tax = (income - 300000) * 0.05
    elif income <= 900000:
        tax = 15000 + (income - 600000) * 0.10
    elif income <= 1200000:
        tax = 45000 + (income - 900000) * 0.15
    elif income <= 1500000:
        tax = 90000 + (income - 1200000) * 0.20
    else:
        tax = 150000 + (income - 1500000) * 0.30

    # Add cess
    tax = tax * 1.04  # 4% health and education cess

    return round(tax, 2)

def get_tax_saving_limit(section: str) -> float:
    """
    Get tax saving limits for different sections
    """
    limits = {
        "80C": 150000,  # PPF, ELSS, LIC, etc.
        "80D": 25000,   # Health insurance premium
        "80E": 0,       # Education loan interest (no limit)
        "80G": 0,       # Donations (varies)
        "80TTA": 10000, # Savings account interest
        "80TTB": 50000, # Senior citizen interest
        "24B": 200000,  # Home loan interest
    }
    return limits.get(section, 0)

from typing import Optional