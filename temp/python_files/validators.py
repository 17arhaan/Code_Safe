"""Data validation functions."""
import re
from typing import Any, List

def is_email(email: str) -> bool:
    """Validate email address."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_phone(phone: str) -> bool:
    """Validate phone number."""
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

def is_url(url: str) -> bool:
    """Validate URL."""
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return re.match(pattern, url) is not None
