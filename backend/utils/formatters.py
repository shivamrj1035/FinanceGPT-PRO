"""
Formatting utilities
"""

from datetime import datetime
from typing import Optional

def format_currency(amount: float, currency: str = "INR") -> str:
    """
    Format amount as currency
    """
    if currency == "INR":
        # Indian numbering system
        if abs(amount) >= 10000000:  # Crore
            return f"₹{amount/10000000:,.2f} Cr"
        elif abs(amount) >= 100000:  # Lakh
            return f"₹{amount/100000:,.2f} L"
        else:
            return f"₹{amount:,.2f}"
    else:
        return f"{currency} {amount:,.2f}"

def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format value as percentage
    """
    return f"{value:.{decimal_places}f}%"

def format_date(date: datetime, format_type: str = "short") -> str:
    """
    Format datetime object
    """
    if format_type == "short":
        return date.strftime("%d-%m-%Y")
    elif format_type == "long":
        return date.strftime("%d %B %Y")
    elif format_type == "full":
        return date.strftime("%d %B %Y, %I:%M %p")
    elif format_type == "iso":
        return date.isoformat()
    else:
        return str(date)

def format_account_number(account_number: str) -> str:
    """
    Mask account number for display
    """
    if len(account_number) <= 4:
        return account_number

    return f"****{account_number[-4:]}"

def format_phone(phone: str) -> str:
    """
    Format Indian phone number
    """
    # Remove all non-digits
    digits = ''.join(filter(str.isdigit, phone))

    if len(digits) == 10:
        return f"+91 {digits[:5]} {digits[5:]}"
    elif len(digits) == 12 and digits.startswith("91"):
        return f"+{digits[:2]} {digits[2:7]} {digits[7:]}"
    else:
        return phone

def format_time_ago(date: datetime) -> str:
    """
    Format datetime as time ago (e.g., "2 hours ago")
    """
    now = datetime.utcnow()
    diff = now - date

    seconds = diff.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24

    if days >= 1:
        return f"{int(days)} day{'s' if days > 1 else ''} ago"
    elif hours >= 1:
        return f"{int(hours)} hour{'s' if hours > 1 else ''} ago"
    elif minutes >= 1:
        return f"{int(minutes)} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"