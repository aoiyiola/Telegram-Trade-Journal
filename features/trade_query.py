"""
Trade query module - List and filter trades
"""
from telegram import Update
from telegram.ext import ContextTypes
import storage
import utils
from features import session_tag, status_rule, user_manager


async def show_open_trades(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display all open trades from user's database (all their accounts)."""
    user_id = update.effective_user.id
    
    # Get all open trades from database
    user_open_trades = storage.get_open_trades(user_id)
    
    if not user_open_trades:
        await update.message.reply_html(
            "📊 <b>Open Trades</b>\n\n"
            "No open trades found.\n\n"
            "💡 Use /newtrade to log a new trade"
        )
        return
    
    # Get user's accounts for display names
    user_config = user_manager.load_user_config(user_id)
    accounts_map = {acc['id']: acc['name'] for acc in user_config['accounts']}
    
    message = f"📊 <b>Open Trades ({len(user_open_trades)})</b>\n"
    message += f"👤 All Your Accounts\n\n"
    
    for trade in user_open_trades:
        account_name = accounts_map.get(trade.get('account_id'), 'Unknown')
        session_display = session_tag.format_session_display(trade['session'])
        status_display = status_rule.format_status_display(trade['status'])
        
        message += (
            f"💼 <b>{account_name}</b> • 🆔 <b>#{trade['trade_id']}</b>\n"
            f"📅 {utils.format_display_datetime(trade['datetime'])}\n"
            f"🌍 {session_display}\n"
            f"💱 <b>{trade['pair']}</b> • {trade['direction']}\n"
            f"💰 Entry: {trade['entry']}\n"
            f"🛑 SL: {trade['sl']} | 🎯 TP: {trade['tp']}\n"
            f"📈 {status_display}\n"
        )
        
        if trade['notes']:
            message += f"📝 <i>{trade['notes'][:50]}...</i>\n" if len(trade['notes']) > 50 else f"📝 <i>{trade['notes']}</i>\n"
        
        message += "\n" + "-"*25 + "\n\n"
    
    message += "✏️ Use /updatetrade to close a trade"
    
    await update.message.reply_html(message)


async def show_recent_trades(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display recent trades from user's database (last 20 trades)."""
    user_id = update.effective_user.id
    
    # Get all trades from database
    user_trades = storage.read_all_trades(user_id)
    
    if not user_trades:
        await update.message.reply_html(
            "📜 <b>Recent Trades</b>\n\n"
            "No trades found.\n\n"
            "💡 Use /newtrade to log your first trade"
        )
        return
    
    # Get user's accounts for display names
    user_config = user_manager.load_user_config(user_id)
    accounts_map = {acc['id']: acc['name'] for acc in user_config['accounts']}
    
    # Get last 20 trades (already sorted newest first by database)
    recent_trades = user_trades[:20]
    
    message = f"📜 <b>Recent Trades (Last {len(recent_trades)})</b>\n"
    message += f"👤 All Your Accounts\n\n"
    
    for trade in recent_trades:
        account_name = accounts_map.get(trade.get('account_id'), 'Unknown')
        session_display = session_tag.format_session_display(trade['session'])
        status_display = status_rule.format_status_display(trade['status'])
        result_display = status_rule.format_result_display(trade['result'])
        
        message += (
            f"💼 <b>{account_name}</b> • 🆔 <b>#{trade['trade_id']}</b>\n"
            f"📅 {utils.format_display_datetime(trade['datetime'])}\n"
            f"🌍 {session_display}\n"
            f"💱 <b>{trade['pair']}</b> • {trade['direction']}\n"
            f"💰 Entry: {trade['entry']}\n"
            f"📈 {status_display} • {result_display}\n"
        )
        
        if trade['notes']:
            message += f"📝 <i>{trade['notes'][:50]}...</i>\n" if len(trade['notes']) > 50 else f"📝 <i>{trade['notes']}</i>\n"
        
        message += "\n" + "-"*25 + "\n\n"
    
    message += (
        "💡 <b>Quick Actions:</b>\n"
        "/opentrades - View open trades only\n"
        "/updatetrade - Update a trade result"
    )
    
    await update.message.reply_html(message)
