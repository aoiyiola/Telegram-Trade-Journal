"""
Session tagging module - Auto-detect trading session based on UK time
"""
from datetime import datetime
import config
import utils


def get_session(dt: datetime = None) -> str:
    """
    Determine the trading session based on UK time.
    
    Sessions:
    - Asia: 00:00 - 06:59
    - London: 07:00 - 12:59
    - New York: 13:00 - 23:59
    
    Args:
        dt: datetime object (optional). If None, uses current UK time.
        
    Returns:
        Session name: 'Asia', 'London', or 'New York'
    """
    hour = utils.get_hour_of_day(dt)
    
    for session_name, (start_hour, end_hour) in config.SESSIONS.items():
        if start_hour <= hour <= end_hour:
            return session_name
    
    # Fallback (should never reach here with current config)
    return 'New York'


def get_session_emoji(session: str) -> str:
    """
    Get emoji representation for a session.
    
    Args:
        session: Session name
        
    Returns:
        Emoji string
    """
    emojis = {
        'Asia': '🌏',
        'London': '🇬🇧',
        'New York': '🇺🇸'
    }
    return emojis.get(session, '📍')


def format_session_display(session: str) -> str:
    """
    Format session with emoji for display.
    
    Args:
        session: Session name
        
    Returns:
        Formatted string like "🇬🇧 London"
    """
    return f"{get_session_emoji(session)} {session}"
