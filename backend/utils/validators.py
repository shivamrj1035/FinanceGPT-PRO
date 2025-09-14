"""
Validation utilities
"""

import re
from typing import Optional

def validate_email(email: str) -> bool:
    """
    Validate email address
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    Validate Indian phone number
    """
    # Remove spaces and hyphens
    phone = phone.replace(" ", "").replace("-", "")

    # Check for Indian phone number format
    pattern = r'^(\+91)?[6-9]\d{9}$'
    return bool(re.match(pattern, phone))

def validate_pan(pan: str) -> bool:
    """
    Validate Indian PAN number
    """
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    return bool(re.match(pattern, pan.upper()))

def validate_aadhar(aadhar: str) -> bool:
    """
    Validate Indian Aadhar number
    """
    # Remove spaces
    aadhar = aadhar.replace(" ", "")

    # Check if 12 digits
    pattern = r'^\d{12}$'
    return bool(re.match(pattern, aadhar))

def validate_amount(amount: float, min_amount: float = 0, max_amount: Optional[float] = None) -> bool:
    """
    Validate transaction amount
    """
    if amount < min_amount:
        return False

    if max_amount and amount > max_amount:
        return False

    return True

def validate_ifsc(ifsc: str) -> bool:
    """
    Validate Indian bank IFSC code
    """
    pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
    return bool(re.match(pattern, ifsc.upper()))

def validate_gst(gst: str) -> bool:
    """
    Validate Indian GST number
    """
    pattern = r'^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$'
    return bool(re.match(pattern, gst.upper()))