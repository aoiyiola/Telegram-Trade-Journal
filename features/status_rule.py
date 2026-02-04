"""
Status rule module - Manages trade status logic
"""


def get_status_from_result(result: str) -> str:
    """
    Determine trade status based on result.
    
    Args:
        result: Trade result ('W', 'L', 'BE', or empty string)
        
    Returns:
        Status: 'OPEN' or 'CLOSED'
    """
    if not result or result.strip() == '':
        return 'OPEN'
    elif result in ['W', 'L', 'BE']:
        return 'CLOSED'
    else:
        return 'OPEN'  # Default for unknown results


def get_status_emoji(status: str) -> str:
    """
    Get emoji representation for a status.
    
    Args:
        status: Status name
        
    Returns:
        Emoji string
    """
    emojis = {
        'OPEN': '🟢',
        'CLOSED': '🔴'
    }
    return emojis.get(status, '⚪')


def get_result_emoji(result: str) -> str:
    """
    Get emoji representation for a result.
    
    Args:
        result: Result code ('W', 'L', 'BE', or empty)
        
    Returns:
        Emoji string
    """
    emojis = {
        'W': '✅',
        'L': '❌',
        'BE': '⚖️',
        '': '⏳'
    }
    return emojis.get(result, '⏳')


def format_status_display(status: str) -> str:
    """
    Format status with emoji for display.
    
    Args:
        status: Status name
        
    Returns:
        Formatted string like "🟢 OPEN"
    """
    return f"{get_status_emoji(status)} {status}"


def format_result_display(result: str) -> str:
    """
    Format result with emoji for display.
    
    Args:
        result: Result code
        
    Returns:
        Formatted string like "✅ W" or "⏳ Pending"
    """
    if not result or result.strip() == '':
        return "⏳ Pending"
    return f"{get_result_emoji(result)} {result}"
