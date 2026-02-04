"""
Utility functions for time handling and ID generation
"""
from datetime import datetime
import config


def get_current_uk_time() -> datetime:
    """
    Get the current time in UK timezone.
    
    Returns:
        datetime object in UK timezone
    """
    return datetime.now(config.TIMEZONE)


def format_datetime(dt: datetime) -> str:
    """
    Format datetime to ISO string for storage.
    
    Args:
        dt: datetime object
        
    Returns:
        ISO formatted datetime string (YYYY-MM-DD HH:MM:SS)
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def get_current_datetime_string() -> str:
    """
    Get current UK time as formatted string.
    
    Returns:
        Current datetime as ISO string
    """
    return format_datetime(get_current_uk_time())


def parse_datetime(datetime_str: str) -> datetime:
    """
    Parse datetime string back to datetime object.
    
    Args:
        datetime_str: ISO formatted datetime string
        
    Returns:
        datetime object with UK timezone
    """
    dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    return config.TIMEZONE.localize(dt)


def get_hour_of_day(dt: datetime = None) -> int:
    """
    Get the hour of day (0-23) for a given datetime.
    If no datetime provided, uses current UK time.
    
    Args:
        dt: datetime object (optional)
        
    Returns:
        Hour of day (0-23)
    """
    if dt is None:
        dt = get_current_uk_time()
    return dt.hour


def format_display_datetime(dt_or_str) -> str:
    """
    Format datetime for user-friendly display.
    
    Args:
        dt_or_str: datetime object or datetime string
        
    Returns:
        Formatted string like "29 Jan 2026, 22:30"
    """
    if isinstance(dt_or_str, str):
        dt = parse_datetime(dt_or_str)
    else:
        dt = dt_or_str
    
    return dt.strftime('%d %b %Y, %H:%M')
