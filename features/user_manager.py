"""
User Manager - Handle user configurations, pairs, and accounts
"""
from typing import List, Dict, Optional
from datetime import datetime
from database import get_db_connection
import config
import utils


def user_exists_in_registry(telegram_id: int) -> bool:
    """
    Check if a user already exists in the database.
    
    Args:
        telegram_id: The user's Telegram ID
        
    Returns:
        True if user exists, False otherwise
    """
    try:
        with get_db_connection() as cursor:
            cursor.execute(
                "SELECT COUNT(*) as count FROM users WHERE telegram_id = %s",
                (telegram_id,)
            )
            result = cursor.fetchone()
            return result['count'] > 0 if result else False
    except Exception as e:
        print(f"❌ Error checking user registry: {e}")
        return False


def register_user(telegram_id: int, username: str, first_name: str, last_name: str, email: Optional[str]) -> bool:
    """
    Register a new user in the database.
    Only inserts if user doesn't already exist.
    
    Args:
        telegram_id: The user's Telegram ID
        username: The user's Telegram username
        first_name: The user's first name
        last_name: The user's last name
        email: The user's email address (optional)
        
    Returns:
        True if user was registered, False if already exists
    """
    try:
        with get_db_connection() as cursor:
            # Use INSERT IGNORE to prevent duplicates (MySQL syntax)
            cursor.execute("""
                INSERT IGNORE INTO users (telegram_id, username, first_name, last_name, email, registration_date, config)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                telegram_id,
                username or '',
                first_name or '',
                last_name or '',
                email or '',
                datetime.now(),
                '{"pairs": ["EURUSD", "GBPUSD", "XAUUSD", "USDJPY"]}'  # Default pairs
            ))
            
            # Check if row was inserted (affected rows > 0)
            if cursor.rowcount > 0:
                user_id = cursor.lastrowid
                
                # Create default account
                cursor.execute("""
                    INSERT INTO accounts (user_id, account_id, account_name, is_default)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, 'main', 'Main Account', True))
                
                # Add default pairs
                default_pairs = ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY']
                for pair in default_pairs:
                    cursor.execute("""
                        INSERT IGNORE INTO pairs (user_id, pair_name)
                        VALUES (%s, %s)
                    """, (user_id, pair))
                
                print(f"✅ User {telegram_id} registered successfully")
                return True
            else:
                print(f"ℹ️ User {telegram_id} already registered - skipping")
                return False
                
    except Exception as e:
        print(f"❌ Error registering user: {e}")
        return False


def load_user_config(telegram_id: int) -> Dict:
    """
    Load user configuration from database.
    
    Returns:
        Dictionary with user_id, email, pairs, accounts, default_account
    """
    try:
        with get_db_connection() as cursor:
            # Get user info
            cursor.execute("""
                SELECT id, telegram_id, email FROM users WHERE telegram_id = %s
            """, (telegram_id,))
            user = cursor.fetchone()
            
            if not user:
                return None
            
            user_id = user['id']
            
            # Get pairs
            cursor.execute("""
                SELECT pair_name FROM pairs WHERE user_id = %s ORDER BY created_at
            """, (user_id,))
            pairs = [row['pair_name'] for row in cursor.fetchall()]
            
            # Get accounts
            cursor.execute("""
                SELECT account_id as id, account_name as name, is_default 
                FROM accounts WHERE user_id = %s ORDER BY created_at
            """, (user_id,))
            accounts = cursor.fetchall()
            
            # Find default account
            default_account = 'main'
            for acc in accounts:
                if acc['is_default']:
                    default_account = acc['id']
                    break
            
            return {
                'user_id': telegram_id,
                'email': user['email'],
                'pairs': pairs,
                'accounts': accounts,
                'default_account': default_account
            }
    except Exception as e:
        print(f"❌ Error loading user config: {e}")
        return None


def save_user_config(telegram_id: int, config_data: Dict) -> None:
    """
    Save user configuration to database.
    (Email updates only - pairs and accounts use dedicated functions)
    """
    try:
        with get_db_connection() as cursor:
            cursor.execute("""
                UPDATE users SET email = %s WHERE telegram_id = %s
            """, (config_data.get('email'), telegram_id))
    except Exception as e:
        print(f"❌ Error saving user config: {e}")


def get_user_pairs(telegram_id: int) -> List[str]:
    """Get list of user's favorite pairs."""
    try:
        with get_db_connection() as cursor:
            cursor.execute("""
                SELECT pair_name FROM pairs 
                WHERE user_id = (SELECT id FROM users WHERE telegram_id = %s)
                ORDER BY created_at
            """, (telegram_id,))
            return [row['pair_name'] for row in cursor.fetchall()]
    except Exception as e:
        print(f"❌ Error getting user pairs: {e}")
        return []


def add_user_pair(telegram_id: int, pair: str) -> bool:
    """
    Add a pair to user's favorites.
    
    Returns:
        True if added, False if already exists
    """
    try:
        pair = pair.upper().strip()
        
        with get_db_connection() as cursor:
            cursor.execute("""
                INSERT IGNORE INTO pairs (user_id, pair_name)
                SELECT id, %s FROM users WHERE telegram_id = %s
            """, (pair, telegram_id))
            
            return cursor.rowcount > 0
    except Exception as e:
        print(f"❌ Error adding pair: {e}")
        return False


def remove_user_pair(telegram_id: int, pair: str) -> bool:
    """
    Remove a pair from user's favorites.
    
    Returns:
        True if removed, False if not found
    """
    try:
        pair = pair.upper().strip()
        
        with get_db_connection() as cursor:
            cursor.execute("""
                DELETE FROM pairs 
                WHERE user_id = (SELECT id FROM users WHERE telegram_id = %s)
                AND pair_name = %s
            """, (telegram_id, pair))
            
            return cursor.rowcount > 0
    except Exception as e:
        print(f"❌ Error removing pair: {e}")
        return False


def get_user_accounts(telegram_id: int) -> List[Dict]:
    """Get list of user's trading accounts."""
    try:
        with get_db_connection() as cursor:
            cursor.execute("""
                SELECT account_id as id, account_name as name, is_default
                FROM accounts 
                WHERE user_id = (SELECT id FROM users WHERE telegram_id = %s)
                ORDER BY created_at
            """, (telegram_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"❌ Error getting user accounts: {e}")
        return []


def get_account_by_id(telegram_id: int, account_id: str) -> Optional[Dict]:
    """Get a specific account by ID."""
    try:
        with get_db_connection() as cursor:
            cursor.execute("""
                SELECT account_id as id, account_name as name, is_default
                FROM accounts 
                WHERE user_id = (SELECT id FROM users WHERE telegram_id = %s)
                AND account_id = %s
            """, (telegram_id, account_id))
            return cursor.fetchone()
    except Exception as e:
        print(f"❌ Error getting account: {e}")
        return None


def add_user_account(telegram_id: int, account_name: str) -> Dict:
    """
    Add a new trading account for user.
    
    Returns:
        The created account dictionary
    """
    try:
        with get_db_connection() as cursor:
            # Get user's existing account count
            cursor.execute("""
                SELECT COUNT(*) as count FROM accounts
                WHERE user_id = (SELECT id FROM users WHERE telegram_id = %s)
            """, (telegram_id,))
            
            count = cursor.fetchone()['count']
            account_id = f'acc{count + 1}'
            
            # Insert new account
            cursor.execute("""
                INSERT INTO accounts (user_id, account_id, account_name, is_default)
                SELECT id, %s, %s, %s FROM users WHERE telegram_id = %s
            """, (account_id, account_name, False, telegram_id))
            
            # Get the created account
            cursor.execute("""
                SELECT account_id, account_name, is_default
                FROM accounts 
                WHERE user_id = (SELECT id FROM users WHERE telegram_id = %s)
                AND account_id = %s
            """, (telegram_id, account_id))
            
            result = cursor.fetchone()
            return {
                'id': result['account_id'],
                'name': result['account_name'],
                'is_default': result['is_default']
            }
    except Exception as e:
        print(f"❌ Error adding account: {e}")
        return None


def remove_user_account(telegram_id: int, account_id: str) -> bool:
    """
    Remove a trading account.
    
    Returns:
        True if removed, False if not found or is last account
    """
    try:
        with get_db_connection() as cursor:
            # Don't allow removing last account
            cursor.execute("""
                SELECT COUNT(*) as count FROM accounts
                WHERE user_id = (SELECT id FROM users WHERE telegram_id = %s)
            """, (telegram_id,))
            
            count = cursor.fetchone()['count']
            if count <= 1:
                return False
            
            # Check if this is the default account
            cursor.execute("""
                SELECT is_default FROM accounts
                WHERE user_id = (SELECT id FROM users WHERE telegram_id = %s)
                AND account_id = %s
            """, (telegram_id, account_id))
            
            account = cursor.fetchone()
            if not account:
                return False
            
            is_default = account['is_default']
            
            # Delete account
            cursor.execute("""
                DELETE FROM accounts
                WHERE user_id = (SELECT id FROM users WHERE telegram_id = %s)
                AND account_id = %s
            """, (telegram_id, account_id))
            
            # If deleted account was default, set first remaining account as default
            if is_default:
                cursor.execute("""
                    UPDATE accounts
                    SET is_default = TRUE
                    WHERE user_id = (SELECT id FROM users WHERE telegram_id = %s)
                    AND id = (
                        SELECT id FROM accounts 
                        WHERE user_id = (SELECT id FROM users WHERE telegram_id = %s)
                        ORDER BY created_at LIMIT 1
                    )
                """, (telegram_id, telegram_id))
            
            return True
    except Exception as e:
        print(f"❌ Error removing account: {e}")
        return False


def rename_user_account(telegram_id: int, account_id: str, new_name: str) -> bool:
    """
    Rename a trading account.
    
    Returns:
        True if renamed, False if account not found
    """
    try:
        with get_db_connection() as cursor:
            cursor.execute("""
                UPDATE accounts
                SET account_name = %s
                WHERE user_id = (SELECT id FROM users WHERE telegram_id = %s)
                AND account_id = %s
            """, (new_name, telegram_id, account_id))
            
            return cursor.rowcount > 0
    except Exception as e:
        print(f"❌ Error renaming account: {e}")
        return False


def get_default_account(telegram_id: int) -> Optional[Dict]:
    """Get user's default account."""
    try:
        with get_db_connection() as cursor:
            cursor.execute("""
                SELECT account_id as id, account_name as name, is_default
                FROM accounts 
                WHERE user_id = (SELECT id FROM users WHERE telegram_id = %s)
                AND is_default = TRUE
            """, (telegram_id,))
            
            result = cursor.fetchone()
            if not result:
                # Fallback to first account
                cursor.execute("""
                    SELECT account_id as id, account_name as name, is_default
                    FROM accounts 
                    WHERE user_id = (SELECT id FROM users WHERE telegram_id = %s)
                    ORDER BY created_at LIMIT 1
                """, (telegram_id,))
                result = cursor.fetchone()
            
            return result
    except Exception as e:
        print(f"❌ Error getting default account: {e}")
        return None


def set_default_account(telegram_id: int, account_id: str) -> bool:
    """
    Set user's default account.
    
    Returns:
        True if set, False if account not found
    """
    try:
        with get_db_connection() as cursor:
            # Verify account exists
            cursor.execute("""
                SELECT id FROM accounts
                WHERE user_id = (SELECT id FROM users WHERE telegram_id = %s)
                AND account_id = %s
            """, (telegram_id, account_id))
            
            if not cursor.fetchone():
                return False
            
            # Clear all defaults for this user
            cursor.execute("""
                UPDATE accounts
                SET is_default = FALSE
                WHERE user_id = (SELECT id FROM users WHERE telegram_id = %s)
            """, (telegram_id,))
            
            # Set new default
            cursor.execute("""
                UPDATE accounts
                SET is_default = TRUE
                WHERE user_id = (SELECT id FROM users WHERE telegram_id = %s)
                AND account_id = %s
            """, (telegram_id, account_id))
            
            return True
    except Exception as e:
        print(f"❌ Error setting default account: {e}")
        return False


# Legacy compatibility functions (no longer used but kept for backward compatibility)
def get_account_csv_path(telegram_id: int, account_id: str) -> Optional[str]:
    """Deprecated: Returns None (CSV no longer used)."""
    return None


def get_global_csv_path(telegram_id: int) -> str:
    """Deprecated: Returns empty string (CSV no longer used)."""
    return ""
