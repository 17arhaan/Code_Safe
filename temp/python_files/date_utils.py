"""Date and time utilities."""
from datetime import datetime, timedelta
from typing import Optional

def get_current_timestamp() -> str:
    """Get current timestamp as string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def parse_date(date_string: str, format_string: str = "%Y-%m-%d") -> Optional[datetime]:
    """Parse date string to datetime object."""
    try:
        return datetime.strptime(date_string, format_string)
    except ValueError:
        return None

def add_days(date: datetime, days: int) -> datetime:
    """Add days to date."""
    return date + timedelta(days=days)

def days_between(date1: datetime, date2: datetime) -> int:
    """Calculate days between two dates."""
    return abs((date2 - date1).days)
