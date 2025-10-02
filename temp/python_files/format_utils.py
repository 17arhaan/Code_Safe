"""Text formatting utilities."""
import re

def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format amount as currency."""
    return f"{currency} ${amount:,.2f}"

def format_phone(phone: str) -> str:
    """Format phone number."""
    cleaned = re.sub(r'\D', '', phone)
    if len(cleaned) == 10:
        return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
    return phone

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
