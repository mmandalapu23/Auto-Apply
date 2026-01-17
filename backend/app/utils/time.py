"""Time utilities."""
from datetime import datetime, timedelta


def parse_date(date_string: str) -> datetime:
    """Parse date string in format YYYY-MM or YYYY-MM-DD."""
    try:
        if len(date_string) == 7:  # YYYY-MM
            return datetime.strptime(date_string, '%Y-%m')
        else:  # YYYY-MM-DD
            return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        return None


def format_date(date: datetime, format_str: str = "%m/%Y") -> str:
    """Format datetime to string."""
    return date.strftime(format_str)


def get_date_range(start_str: str, end_str: str = None) -> str:
    """Get readable date range."""
    start = parse_date(start_str)
    if end_str:
        end = parse_date(end_str)
        return f"{format_date(start)} - {format_date(end)}"
    else:
        return f"{format_date(start)} - Present"


def calculate_months_duration(start_str: str, end_str: str) -> int:
    """Calculate duration in months."""
    start = parse_date(start_str)
    end = parse_date(end_str)
    if not start or not end:
        return 0
    
    return (end.year - start.year) * 12 + (end.month - start.month)


def is_date_range_valid(start_str: str, end_str: str) -> bool:
    """Check if date range is valid (start <= end)."""
    start = parse_date(start_str)
    end = parse_date(end_str)
    if not start or not end:
        return False
    return start <= end
