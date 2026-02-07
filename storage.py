"""
Storage module for database-based trade data management
"""
from typing import List, Dict, Optional
from datetime import datetime
from database import get_db_connection
import config


def get_user_id_from_telegram(telegram_id: int) -> Optional[int]:
    """Get internal user ID from telegram ID."""
    try:
        with get_db_connection() as cursor:
            cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
            result = cursor.fetchone()
            return result['id'] if result else None
    except Exception as e:
        print(f"Error getting user ID: {e}")
        return None


def save_trade(trade_data: Dict, telegram_id: int) -> bool:
    """
    Save a new trade to database.
    
    Args:
        trade_data: Dictionary containing all trade fields
        telegram_id: User's Telegram ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        user_id = get_user_id_from_telegram(telegram_id)
        if not user_id:
            print(f"User not found: {telegram_id}")
            return False
        
        with get_db_connection() as cursor:
            cursor.execute("""
                INSERT INTO trades (
                    trade_id, user_id, account_id, pair, direction,
                    entry_price, stop_loss, take_profit, status, result,
                    session, news_risk, notes, entry_datetime, exit_datetime
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                trade_data['trade_id'],
                user_id,
                trade_data.get('account_id', 'main'),
                trade_data['pair'],
                trade_data['direction'],
                trade_data['entry'],
                trade_data.get('sl') or trade_data.get('stop_loss'),
                trade_data.get('tp') or trade_data.get('take_profit'),
                trade_data.get('status', 'OPEN'),
                trade_data.get('result', ''),
                trade_data.get('session', ''),
                trade_data.get('news_risk', ''),
                trade_data.get('notes', ''),
                trade_data.get('datetime') or trade_data.get('entry_datetime', datetime.now()),
                trade_data.get('exit_datetime')
            ))
        return True
    except Exception as e:
        print(f"Error saving trade: {e}")
        return False


def read_all_trades(telegram_id: int) -> List[Dict]:
    """
    Read all trades for a user from database.
    
    Args:
        telegram_id: User's Telegram ID
        
    Returns:
        List of trade dictionaries
    """
    try:
        user_id = get_user_id_from_telegram(telegram_id)
        if not user_id:
            return []
        
        with get_db_connection() as cursor:
            cursor.execute("""
                SELECT 
                    trade_id, account_id, pair, direction,
                    entry_price as entry, stop_loss as sl, take_profit as tp,
                    status, result, session, news_risk, notes,
                    entry_datetime as datetime, exit_datetime
                FROM trades
                WHERE user_id = %s
                ORDER BY entry_datetime DESC
            """, (user_id,))
            
            trades = cursor.fetchall()
            # Convert datetime objects to strings for compatibility
            for trade in trades:
                if trade['datetime']:
                    trade['datetime'] = trade['datetime'].strftime('%Y-%m-%d %H:%M:%S')
                if trade['exit_datetime']:
                    trade['exit_datetime'] = trade['exit_datetime'].strftime('%Y-%m-%d %H:%M:%S')
            
            return trades
    except Exception as e:
        print(f"Error reading trades: {e}")
        return []


def get_trade_by_id(trade_id: str, telegram_id: int) -> Optional[Dict]:
    """
    Get a specific trade by ID.
    
    Args:
        trade_id: The trade ID to search for
        telegram_id: User's Telegram ID
        
    Returns:
        Trade dictionary if found, None otherwise
    """
    try:
        user_id = get_user_id_from_telegram(telegram_id)
        if not user_id:
            return None
        
        with get_db_connection() as cursor:
            cursor.execute("""
                SELECT 
                    trade_id, account_id, pair, direction,
                    entry_price as entry, stop_loss as sl, take_profit as tp,
                    status, result, session, news_risk, notes,
                    entry_datetime as datetime, exit_datetime
                FROM trades
                WHERE trade_id = %s AND user_id = %s
            """, (trade_id, user_id))
            
            trade = cursor.fetchone()
            if trade:
                if trade['datetime']:
                    trade['datetime'] = trade['datetime'].strftime('%Y-%m-%d %H:%M:%S')
                if trade['exit_datetime']:
                    trade['exit_datetime'] = trade['exit_datetime'].strftime('%Y-%m-%d %H:%M:%S')
            return trade
    except Exception as e:
        print(f"Error getting trade: {e}")
        return None


def update_trade(trade_id: str, updates: Dict, telegram_id: int) -> bool:
    """
    Update an existing trade with new data.
    
    Args:
        trade_id: The ID of the trade to update
        updates: Dictionary of fields to update
        telegram_id: User's Telegram ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        user_id = get_user_id_from_telegram(telegram_id)
        if not user_id:
            return False
        
        # Build dynamic UPDATE query based on provided fields
        set_clauses = []
        values = []
        
        field_mapping = {
            'result': 'result',
            'status': 'status',
            'exit_datetime': 'exit_datetime',
            'notes': 'notes',
            'sl': 'stop_loss',
            'tp': 'take_profit',
            'entry': 'entry_price',
            'session': 'session',
            'news_risk': 'news_risk'
        }
        
        for key, db_field in field_mapping.items():
            if key in updates:
                set_clauses.append(f"{db_field} = %s")
                values.append(updates[key])
        
        if not set_clauses:
            return False
        
        # Add updated_at timestamp
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        
        # Add WHERE clause values
        values.extend([trade_id, user_id])
        
        with get_db_connection() as cursor:
            query = f"""
                UPDATE trades 
                SET {', '.join(set_clauses)}
                WHERE trade_id = %s AND user_id = %s
            """
            cursor.execute(query, values)
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating trade: {e}")
        return False


def get_open_trades(telegram_id: int) -> List[Dict]:
    """
    Get all open trades for a user.
    
    Args:
        telegram_id: User's Telegram ID
    
    Returns:
        List of open trades
    """
    try:
        user_id = get_user_id_from_telegram(telegram_id)
        if not user_id:
            return []
        
        with get_db_connection() as cursor:
            cursor.execute("""
                SELECT 
                    trade_id, account_id, pair, direction,
                    entry_price as entry, stop_loss as sl, take_profit as tp,
                    status, result, session, news_risk, notes,
                    entry_datetime as datetime, exit_datetime
                FROM trades
                WHERE user_id = %s AND status = 'OPEN'
                ORDER BY entry_datetime DESC
            """, (user_id,))
            
            trades = cursor.fetchall()
            for trade in trades:
                if trade['datetime']:
                    trade['datetime'] = trade['datetime'].strftime('%Y-%m-%d %H:%M:%S')
            return trades
    except Exception as e:
        print(f"Error getting open trades: {e}")
        return []


def get_recent_trades(limit: int = 10, telegram_id: int = None) -> List[Dict]:
    """
    Get the most recent trades for a user.
    
    Args:
        limit: Maximum number of trades to return
        telegram_id: User's Telegram ID
        
    Returns:
        List of recent trades (newest first)
    """
    try:
        user_id = get_user_id_from_telegram(telegram_id)
        if not user_id:
            return []
        
        with get_db_connection() as cursor:
            cursor.execute("""
                SELECT 
                    trade_id, account_id, pair, direction,
                    entry_price as entry, stop_loss as sl, take_profit as tp,
                    status, result, session, news_risk, notes,
                    entry_datetime as datetime, exit_datetime
                FROM trades
                WHERE user_id = %s
                ORDER BY entry_datetime DESC
                LIMIT %s
            """, (user_id, limit))
            
            trades = cursor.fetchall()
            for trade in trades:
                if trade['datetime']:
                    trade['datetime'] = trade['datetime'].strftime('%Y-%m-%d %H:%M:%S')
                if trade['exit_datetime']:
                    trade['exit_datetime'] = trade['exit_datetime'].strftime('%Y-%m-%d %H:%M:%S')
            return trades
    except Exception as e:
        print(f"Error getting recent trades: {e}")
        return []


def get_next_trade_id(telegram_id: int) -> str:
    """
    Get the next available trade ID for a user.
    
    Args:
        telegram_id: User's Telegram ID
    
    Returns:
        Next trade ID (format: T1, T2, T3, etc.)
    """
    try:
        user_id = get_user_id_from_telegram(telegram_id)
        if not user_id:
            return "T1"
        
        with get_db_connection() as cursor:
            cursor.execute("""
                SELECT trade_id FROM trades
                WHERE user_id = %s
                ORDER BY id DESC
                LIMIT 1
            """, (user_id,))
            
            result = cursor.fetchone()
            if not result:
                return "T1"
            
            # Extract number from trade_id (e.g., "T5" -> 5)
            last_id = result['trade_id']
            if last_id.startswith('T'):
                num = int(last_id[1:])
                return f"T{num + 1}"
            return "T1"
    except Exception as e:
        print(f"Error getting next trade ID: {e}")
        return "T1"
