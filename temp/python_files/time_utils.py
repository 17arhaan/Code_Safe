"""Time and date utilities."""
from datetime import datetime, timedelta

def get_timestamp() -> str:
    """Get current timestamp as string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def add_days(date: datetime, days: int) -> datetime:
    """Add days to a date."""
    return date + timedelta(days=days)

def days_between(date1: datetime, date2: datetime) -> int:
    """Calculate days between two dates."""
    return abs((date2 - date1).days)
