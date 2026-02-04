"""
User Manager - Handle user configurations, pairs, and accounts
"""
import json
import os
from typing import List, Dict, Optional
import config


def get_user_config_path(user_id: int) -> str:
    """Get the path to a user's config file."""
    user_data_dir = os.path.join(os.path.dirname(config.DATA_DIR), 'user_data')
    os.makedirs(user_data_dir, exist_ok=True)
    return os.path.join(user_data_dir, f'user_{user_id}_config.json')


def get_user_data_dir(user_id: int) -> str:
    """Get the path to a user's data directory."""
    user_dir = os.path.join(config.DATA_DIR, f'user_{user_id}')
    os.makedirs(user_dir, exist_ok=True)
    return user_dir


def load_user_config(user_id: int) -> Dict:
    """
    Load user configuration from file.
    
    Returns:
        Dictionary with user_id, pairs, accounts, default_account
    """
    config_path = get_user_config_path(user_id)
    
    if not os.path.exists(config_path):
        # Create default config for new user
        # Ensure user data directory exists
        user_dir = get_user_data_dir(user_id)
        
        default_config = {
            'user_id': user_id,
            'pairs': ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY'],  # Default pairs
            'accounts': [
                {
                    'id': 'main',
                    'name': 'Main Account',
                    'csv_path': os.path.join(user_dir, 'account_main.csv')
                }
            ],
            'default_account': 'main'
        }
        save_user_config(user_id, default_config)
        return default_config
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # Return default if file is corrupted
        user_dir = get_user_data_dir(user_id)
        return {
            'user_id': user_id,
            'pairs': ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY'],
            'accounts': [
                {
                    'id': 'main',
                    'name': 'Main Account',
                    'csv_path': os.path.join(user_dir, 'account_main.csv')
                }
            ],
            'default_account': 'main'
        }


def save_user_config(user_id: int, config_data: Dict) -> None:
    """Save user configuration to file."""
    config_path = get_user_config_path(user_id)
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)


def get_user_pairs(user_id: int) -> List[str]:
    """Get list of user's favorite pairs."""
    config = load_user_config(user_id)
    return config.get('pairs', [])


def add_user_pair(user_id: int, pair: str) -> bool:
    """
    Add a pair to user's favorites.
    
    Returns:
        True if added, False if already exists
    """
    config = load_user_config(user_id)
    pairs = config.get('pairs', [])
    
    pair = pair.upper().strip()
    
    if pair in pairs:
        return False
    
    pairs.append(pair)
    config['pairs'] = pairs
    save_user_config(user_id, config)
    return True


def remove_user_pair(user_id: int, pair: str) -> bool:
    """
    Remove a pair from user's favorites.
    
    Returns:
        True if removed, False if not found
    """
    config = load_user_config(user_id)
    pairs = config.get('pairs', [])
    
    pair = pair.upper().strip()
    
    if pair not in pairs:
        return False
    
    pairs.remove(pair)
    config['pairs'] = pairs
    save_user_config(user_id, config)
    return True


def get_user_accounts(user_id: int) -> List[Dict]:
    """Get list of user's trading accounts."""
    config = load_user_config(user_id)
    return config.get('accounts', [])


def get_account_by_id(user_id: int, account_id: str) -> Optional[Dict]:
    """Get a specific account by ID."""
    accounts = get_user_accounts(user_id)
    for account in accounts:
        if account['id'] == account_id:
            return account
    return None


def add_user_account(user_id: int, account_name: str) -> Dict:
    """
    Add a new trading account for user.
    
    Returns:
        The created account dictionary
    """
    config = load_user_config(user_id)
    accounts = config.get('accounts', [])
    
    # Generate unique account ID
    account_id = f'acc{len(accounts) + 1}'
    
    # Get user's data directory
    user_dir = get_user_data_dir(user_id)
    
    new_account = {
        'id': account_id,
        'name': account_name,
        'csv_path': os.path.join(user_dir, f'account_{account_id}.csv')
    }
    
    accounts.append(new_account)
    config['accounts'] = accounts
    save_user_config(user_id, config)
    
    return new_account


def remove_user_account(user_id: int, account_id: str) -> bool:
    """
    Remove a trading account.
    
    Returns:
        True if removed, False if not found or is last account
    """
    config = load_user_config(user_id)
    accounts = config.get('accounts', [])
    
    # Don't allow removing last account
    if len(accounts) <= 1:
        return False
    
    # Find and remove account
    for i, account in enumerate(accounts):
        if account['id'] == account_id:
            accounts.pop(i)
            config['accounts'] = accounts
            
            # Update default if removed account was default
            if config.get('default_account') == account_id:
                config['default_account'] = accounts[0]['id']
            
            save_user_config(user_id, config)
            return True
    
    return False


def rename_user_account(user_id: int, account_id: str, new_name: str) -> bool:
    """
    Rename a trading account.
    
    Returns:
        True if renamed, False if account not found
    """
    config = load_user_config(user_id)
    accounts = config.get('accounts', [])
    
    for account in accounts:
        if account['id'] == account_id:
            account['name'] = new_name
            config['accounts'] = accounts
            save_user_config(user_id, config)
            return True
    
    return False


def get_default_account(user_id: int) -> Optional[Dict]:
    """Get user's default account."""
    config = load_user_config(user_id)
    default_id = config.get('default_account')
    
    if not default_id:
        accounts = config.get('accounts', [])
        if accounts:
            return accounts[0]
        return None
    
    return get_account_by_id(user_id, default_id)


def set_default_account(user_id: int, account_id: str) -> bool:
    """
    Set user's default account.
    
    Returns:
        True if set, False if account not found
    """
    # Verify account exists
    account = get_account_by_id(user_id, account_id)
    if not account:
        return False
    
    config = load_user_config(user_id)
    config['default_account'] = account_id
    save_user_config(user_id, config)
    return True


def get_account_csv_path(user_id: int, account_id: str) -> Optional[str]:
    """Get the CSV file path for a specific account."""
    account = get_account_by_id(user_id, account_id)
    if account:
        return account['csv_path']
    return None


def get_global_csv_path(user_id: int) -> str:
    """Get the path to the user's personal global trades CSV."""
    user_dir = get_user_data_dir(user_id)
    return os.path.join(user_dir, 'global.csv')
