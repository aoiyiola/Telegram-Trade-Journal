"""
Storage module for CSV-based trade data management
"""
import csv
import os
from typing import List, Dict, Optional
import config


# CSV Headers as per schema
CSV_HEADERS = [
    'trade_id',
    'datetime',
    'pair',
    'direction',
    'entry',
    'sl',
    'tp',
    'session',
    'status',
    'news_risk',
    'result',
    'notes'
]

# Global CSV has additional column for account tracking (per-user global)
GLOBAL_CSV_HEADERS = [
    'trade_id',
    'account_id',
    'datetime',
    'pair',
    'direction',
    'entry',
    'sl',
    'tp',
    'session',
    'status',
    'news_risk',
    'result',
    'notes'
]


def init_csv(csv_path: str = None, is_global: bool = False) -> None:
    """Initialize CSV file with headers if it doesn't exist."""
    if csv_path is None:
        csv_path = config.TRADES_CSV_PATH
    
    if not os.path.exists(csv_path):
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        headers = GLOBAL_CSV_HEADERS if is_global else CSV_HEADERS
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()


def read_all_trades(csv_path: str = None) -> List[Dict]:
    """
    Read all trades from CSV.
    Returns a list of dictionaries, each representing a trade.
    """
    if csv_path is None:
        csv_path = config.TRADES_CSV_PATH
    
    init_csv(csv_path)  # Ensure file exists
    
    trades = []
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            row['trade_id'] = int(row['trade_id'])
            row['entry'] = float(row['entry'])
            row['sl'] = float(row['sl'])
            row['tp'] = float(row['tp'])
            trades.append(row)
    
    return trades


def save_trade(trade_data: Dict, csv_path: str = None, is_global: bool = False) -> bool:
    """
    Save a new trade to CSV.
    
    Args:
        trade_data: Dictionary containing all trade fields
        csv_path: Path to CSV file (optional, defaults to main CSV)
        is_global: Whether this is the global CSV (has extra columns)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if csv_path is None:
            csv_path = config.TRADES_CSV_PATH
        
        init_csv(csv_path, is_global=is_global)  # Ensure file exists
        
        headers = GLOBAL_CSV_HEADERS if is_global else CSV_HEADERS
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
            writer.writerow(trade_data)
        
        return True
    except Exception as e:
        print(f"Error saving trade: {e}")
        return False


def get_trade_by_id(trade_id: int, csv_path: str = None) -> Optional[Dict]:
    """
    Get a specific trade by ID.
    
    Args:
        trade_id: The trade ID to search for
        csv_path: Path to CSV file (optional)
        
    Returns:
        Trade dictionary if found, None otherwise
    """
    trades = read_all_trades(csv_path)
    for trade in trades:
        if trade['trade_id'] == trade_id:
            return trade
    return None


def update_trade(trade_id: int, updates: Dict, csv_path: str = None) -> bool:
    """
    Update an existing trade with new data.
    
    Args:
        trade_id: The ID of the trade to update
        updates: Dictionary of fields to update
        csv_path: Path to CSV file (optional)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if csv_path is None:
            csv_path = config.TRADES_CSV_PATH
        
        trades = read_all_trades(csv_path)
        updated = False
        
        for trade in trades:
            if trade['trade_id'] == trade_id:
                trade.update(updates)
                updated = True
                break
        
        if not updated:
            return False
        
        # Write all trades back to CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(trades)
        
        return True
    except Exception as e:
        print(f"Error updating trade: {e}")
        return False


def get_open_trades(csv_path: str = None) -> List[Dict]:
    """
    Get all trades with empty result field (open trades).
    
    Args:
        csv_path: Path to CSV file (optional)
    
    Returns:
        List of open trades
    """
    trades = read_all_trades(csv_path)
    return [trade for trade in trades if not trade['result'].strip()]


def get_recent_trades(limit: int = 10, csv_path: str = None) -> List[Dict]:
    """
    Get the most recent trades.
    
    Args:
        limit: Maximum number of trades to return
        csv_path: Path to CSV file (optional)
        
    Returns:
        List of recent trades (newest first)
    """
    trades = read_all_trades(csv_path)
    # Sort by trade_id descending (most recent first)
    trades.sort(key=lambda x: x['trade_id'], reverse=True)
    return trades[:limit]


def get_next_trade_id(csv_path: str = None) -> int:
    """
    Get the next available trade ID.
    
    Args:
        csv_path: Path to CSV file (optional)
    
    Returns:
        Next trade ID (1 if no trades exist, otherwise max_id + 1)
    """
    trades = read_all_trades(csv_path)
    if not trades:
        return 1
    return max(trade['trade_id'] for trade in trades) + 1
