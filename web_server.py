"""
Web Dashboard API Server
Provides REST API endpoints for the trading journal dashboard
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import secrets
from datetime import datetime, timedelta
import os
from database import get_db_connection
import config

app = Flask(__name__, static_folder='web/dist')
CORS(app)

# Store active dashboard tokens (in production, use Redis or database)
active_tokens = {}
user_tokens = {}  # Maps telegram_id -> active token for reuse


def generate_dashboard_token(telegram_id: int, expires_hours: int = 24) -> str:
    """
    Generate or reuse a secure token for dashboard access.
    One token per user - reuses if still valid, generates new if expired.
    """
    # Check if user already has a valid token
    if telegram_id in user_tokens:
        existing_token = user_tokens[telegram_id]
        if existing_token in active_tokens:
            token_data = active_tokens[existing_token]
            # If token still valid for at least 1 hour, reuse it
            if datetime.now() + timedelta(hours=1) < token_data['expires']:
                print(f"♻️ Reusing existing token for user {telegram_id}")
                return existing_token
            else:
                # Token expiring soon, clean it up
                print(f"🧹 Cleaning up expiring token for user {telegram_id}")
                del active_tokens[existing_token]
                del user_tokens[telegram_id]
    
    # Generate new token
    token = secrets.token_urlsafe(32)
    expiry = datetime.now() + timedelta(hours=expires_hours)
    active_tokens[token] = {
        'telegram_id': telegram_id,
        'expires': expiry
    }
    user_tokens[telegram_id] = token
    print(f"🔑 Generated new token for user {telegram_id}")
    return token


def verify_token(token: str) -> int:
    """Verify token and return telegram_id, or None if invalid."""
    if token not in active_tokens:
        return None
    
    token_data = active_tokens[token]
    if datetime.now() > token_data['expires']:
        # Token expired - clean up
        telegram_id = token_data['telegram_id']
        del active_tokens[token]
        if telegram_id in user_tokens and user_tokens[telegram_id] == token:
            del user_tokens[telegram_id]
        print(f"🧹 Cleaned up expired token for user {telegram_id}")
        return None
    
    return token_data['telegram_id']


def cleanup_expired_tokens():
    """Remove all expired tokens from memory."""
    now = datetime.now()
    expired_tokens = [
        token for token, data in active_tokens.items()
        if now > data['expires']
    ]
    
    for token in expired_tokens:
        telegram_id = active_tokens[token]['telegram_id']
        del active_tokens[token]
        if telegram_id in user_tokens and user_tokens[telegram_id] == token:
            del user_tokens[telegram_id]
    
    if expired_tokens:
        print(f"🧹 Cleaned up {len(expired_tokens)} expired tokens")
    return len(expired_tokens)


@app.route('/api/dashboard/<token>')
def get_dashboard_data(token):
    """Get complete dashboard data for a user."""
    telegram_id = verify_token(token)
    if not telegram_id:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    try:
        with get_db_connection() as cursor:
            # Get user info
            cursor.execute("""
                SELECT id, telegram_id, username, first_name, email
                FROM users WHERE telegram_id = %s
            """, (telegram_id,))
            user = cursor.fetchone()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            user_id = user['id']
            
            # Get all trades
            cursor.execute("""
                SELECT * FROM trades 
                WHERE user_id = %s 
                ORDER BY entry_datetime DESC
            """, (user_id,))
            trades = cursor.fetchall()
            
            # Calculate statistics
            total_trades = len(trades)
            closed_trades = [t for t in trades if t['status'] == 'CLOSED']
            open_trades = [t for t in trades if t['status'] == 'OPEN']
            
            wins = len([t for t in closed_trades if t['result'] == 'W'])
            losses = len([t for t in closed_trades if t['result'] == 'L'])
            break_even = len([t for t in closed_trades if t['result'] == 'BE'])
            
            win_rate = (wins / len(closed_trades) * 100) if closed_trades else 0
            
            # Group by pair
            pair_stats = {}
            for trade in trades:
                pair = trade['pair']
                if pair not in pair_stats:
                    pair_stats[pair] = {
                        'total': 0,
                        'wins': 0,
                        'losses': 0,
                        'win_rate': 0
                    }
                pair_stats[pair]['total'] += 1
                if trade['result'] == 'W':
                    pair_stats[pair]['wins'] += 1
                elif trade['result'] == 'L':
                    pair_stats[pair]['losses'] += 1
            
            # Calculate win rates
            for pair in pair_stats:
                closed = pair_stats[pair]['wins'] + pair_stats[pair]['losses']
                if closed > 0:
                    pair_stats[pair]['win_rate'] = (pair_stats[pair]['wins'] / closed * 100)
            
            # Group by session
            session_stats = {}
            for trade in trades:
                session = trade['session'] or 'Unknown'
                if session not in session_stats:
                    session_stats[session] = {
                        'total': 0,
                        'wins': 0,
                        'losses': 0,
                        'win_rate': 0
                    }
                session_stats[session]['total'] += 1
                if trade['result'] == 'W':
                    session_stats[session]['wins'] += 1
                elif trade['result'] == 'L':
                    session_stats[session]['losses'] += 1
            
            # Calculate session win rates
            for session in session_stats:
                closed = session_stats[session]['wins'] + session_stats[session]['losses']
                if closed > 0:
                    session_stats[session]['win_rate'] = (session_stats[session]['wins'] / closed * 100)
            
            # Get accounts
            cursor.execute("""
                SELECT account_id, account_name, is_default
                FROM accounts WHERE user_id = %s
            """, (user_id,))
            accounts = cursor.fetchall()
            
            # Calculate user initials
            name = user['first_name'] or user['username'] or 'User'
            name_parts = name.split()
            initials = ''.join([part[0].upper() for part in name_parts if part])[:2]
            if len(initials) < 2 and len(name) > 0:
                initials = name[0:2].upper()
            
            # Calculate comprehensive trading metrics
            # Sort closed trades by exit date for time-series
            closed_trades_sorted = sorted(
                [t for t in closed_trades if t['exit_datetime']], 
                key=lambda x: x['exit_datetime']
            )
            
            # Build equity curve (cumulative P&L)
            equity_curve = []
            cumulative_pnl = 0
            for trade in closed_trades_sorted:
                # Calculate P&L (simplified - using pips or percentage)
                pnl = 0
                if trade['result'] == 'W':
                    pnl = 1  # Win
                elif trade['result'] == 'L':
                    pnl = -1  # Loss
                # For break-even, pnl stays 0
                
                cumulative_pnl += pnl
                equity_curve.append({
                    'date': trade['exit_datetime'].strftime('%Y-%m-%d'),
                    'timestamp': trade['exit_datetime'].isoformat(),
                    'pnl': pnl,
                    'cumulative': cumulative_pnl,
                    'trade_id': trade['trade_id']
                })
            
            # Calculate win/loss streaks
            current_streak = 0
            current_streak_type = None
            max_win_streak = 0
            max_loss_streak = 0
            
            for trade in closed_trades_sorted:
                if trade['result'] == 'W':
                    if current_streak_type == 'W':
                        current_streak += 1
                    else:
                        current_streak = 1
                        current_streak_type = 'W'
                    max_win_streak = max(max_win_streak, current_streak)
                elif trade['result'] == 'L':
                    if current_streak_type == 'L':
                        current_streak += 1
                    else:
                        current_streak = 1
                        current_streak_type = 'L'
                    max_loss_streak = max(max_loss_streak, current_streak)
                else:  # Break-even resets streak
                    current_streak = 0
                    current_streak_type = None
            
            # Calculate profit factor and expectancy
            total_wins = wins
            total_losses = losses
            avg_win = total_wins / wins if wins > 0 else 0
            avg_loss = total_losses / losses if losses > 0 else 0
            profit_factor = (total_wins / total_losses) if total_losses > 0 else float('inf')
            expectancy = (avg_win * win_rate / 100) - (avg_loss * (100 - win_rate) / 100) if closed_trades else 0
            
            # Calculate per-account statistics
            account_stats = {}
            for account in accounts:
                acc_id = account['account_id']
                acc_trades = [t for t in trades if t['account_id'] == acc_id]
                acc_closed = [t for t in acc_trades if t['status'] == 'CLOSED']
                acc_wins = len([t for t in acc_closed if t['result'] == 'W'])
                acc_losses = len([t for t in acc_closed if t['result'] == 'L'])
                acc_be = len([t for t in acc_closed if t['result'] == 'BE'])
                
                account_stats[acc_id] = {
                    'account_name': account['account_name'],
                    'is_default': account['is_default'],
                    'total_trades': len(acc_trades),
                    'closed_trades': len(acc_closed),
                    'open_trades': len([t for t in acc_trades if t['status'] == 'OPEN']),
                    'wins': acc_wins,
                    'losses': acc_losses,
                    'break_even': acc_be,
                    'win_rate': (acc_wins / len(acc_closed) * 100) if acc_closed else 0
                }
            
            # Format trades for response
            formatted_trades = []
            for trade in trades[:100]:  # Last 100 trades
                formatted_trades.append({
                    'id': trade['trade_id'],
                    'pair': trade['pair'],
                    'direction': trade['direction'],
                    'entry_price': float(trade['entry_price']),
                    'stop_loss': float(trade['stop_loss']) if trade['stop_loss'] else None,
                    'take_profit': float(trade['take_profit']) if trade['take_profit'] else None,
                    'status': trade['status'],
                    'result': trade['result'],
                    'session': trade['session'],
                    'news_risk': trade['news_risk'],
                    'entry_datetime': trade['entry_datetime'].isoformat() if trade['entry_datetime'] else None,
                    'exit_datetime': trade['exit_datetime'].isoformat() if trade['exit_datetime'] else None,
                    'account': trade['account_id']
                })
            
            return jsonify({
                'user': {
                    'telegram_id': user['telegram_id'],
                    'username': user['username'],
                    'name': user['first_name'],
                    'email': user['email'],
                    'initials': initials
                },
                'stats': {
                    'total_trades': total_trades,
                    'open_trades': len(open_trades),
                    'closed_trades': len(closed_trades),
                    'wins': wins,
                    'losses': losses,
                    'break_even': break_even,
                    'win_rate': round(win_rate, 2),
                    'max_win_streak': max_win_streak,
                    'max_loss_streak': max_loss_streak,
                    'profit_factor': round(profit_factor, 2) if profit_factor != float('inf') else 'N/A',
                    'expectancy': round(expectancy, 2)
                },
                'equity_curve': equity_curve,
                'pair_stats': pair_stats,
                'session_stats': session_stats,
                'account_stats': account_stats,
                'accounts': [{'account_id': a['account_id'], 'account_name': a['account_name'], 'is_default': a['is_default']} for a in accounts],
                'recent_trades': formatted_trades
            })
            
    except Exception as e:
        print(f"❌ Dashboard API error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve React app."""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
