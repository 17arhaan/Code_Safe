"""Data validation utilities."""
from typing import Any, List

def validate_email(email: str) -> bool:
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    import re
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone))

def validate_required_fields(data: dict, required_fields: List[str]) -> bool:
    """Validate that all required fields are present."""
    return all(field in data for field in required_fields)
