"""
Trade update module - Update trade results (W/L/BE)
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
import storage
from features import status_rule, user_manager


# Conversation states
SELECT_TRADE, SELECT_RESULT = range(2)


async def start_update_trade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the trade update conversation - show open trades from user's global CSV."""
    user_id = update.effective_user.id
    
    # Get open trades from user's personal global CSV
    global_csv_path = user_manager.get_global_csv_path(user_id)
    open_trades = storage.get_open_trades(global_csv_path)
    
    if not open_trades:
        await update.message.reply_html(
            "✏️ <b>Update Trade</b>\n\n"
            "No open trades to update.\n\n"
            "💡 Use /newtrade to log a new trade"
        )
        return ConversationHandler.END
    
    # Create inline keyboard with open trades
    keyboard = []
    for trade in open_trades[:10]:  # Limit to 10 to avoid keyboard size limits
        # Include account name for clarity
        button_text = f"#{trade['trade_id']} - {trade['pair']} {trade['direction']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"trade_{trade['trade_id']}_{trade.get('account_id', '')}")])
    
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="trade_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(
        "✏️ <b>Update Trade Result</b>\n\n"
        f"You have <b>{len(open_trades)}</b> open trade(s).\n"
        "Select a trade to update:",
        reply_markup=reply_markup
    )
    return SELECT_TRADE


async def receive_trade_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive selected trade and show result options."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "trade_cancel":
        await query.edit_message_text("❌ Update cancelled.")
        return ConversationHandler.END
    
    # Extract trade ID and account ID from callback data
    parts = query.data.split('_')
    trade_id = int(parts[1])
    account_id = parts[2] if len(parts) > 2 else None
    
    context.user_data['update_trade_id'] = trade_id
    context.user_data['update_account_id'] = account_id
    
    # Get trade details from user's global CSV
    global_csv_path = user_manager.get_global_csv_path(update.effective_user.id)
    all_trades = storage.read_all_trades(global_csv_path)
    trade = next((t for t in all_trades if int(t['trade_id']) == trade_id), None)
    
    if not trade:
        await query.edit_message_text("❌ Trade not found.")
        return ConversationHandler.END
    
    # Create result selection keyboard
    keyboard = [
        [
            InlineKeyboardButton("✅ Win (W)", callback_data="result_W"),
            InlineKeyboardButton("❌ Loss (L)", callback_data="result_L"),
        ],
        [
            InlineKeyboardButton("⚖️ BreakEven (BE)", callback_data="result_BE"),
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="result_back"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✏️ <b>Update Trade #{trade_id}</b>\n\n"
        f"💱 Pair: <b>{trade['pair']}</b>\n"
        f"📊 Direction: <b>{trade['direction']}</b>\n"
        f"💰 Entry: <b>{trade['entry']}</b>\n"
        f"🛑 SL: {trade['sl']} | 🎯 TP: {trade['tp']}\n\n"
        "Select the trade result:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    return SELECT_RESULT


async def receive_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and save the trade result to both CSVs."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "result_back":
        # Go back to trade selection
        context.user_data.clear()
        await query.edit_message_text("Going back...")
        # Restart the process
        await start_update_trade(update, context)
        return SELECT_TRADE
    
    # Extract result
    result = query.data.split('_')[1]  # "result_W" -> "W"
    trade_id = context.user_data['update_trade_id']
    account_id = context.user_data.get('update_account_id')
    user_id = update.effective_user.id
    
    # Calculate new status
    new_status = status_rule.get_status_from_result(result)
    
    updates = {
        'result': result,
        'status': new_status
    }
    
    # Update in user's global CSV
    global_csv_path = user_manager.get_global_csv_path(user_id)
    success_global = storage.update_trade(trade_id, updates, global_csv_path)
    
    # Update in account CSV
    account_csv_path = user_manager.get_account_csv_path(user_id, account_id)
    success_account = storage.update_trade(trade_id, updates, account_csv_path)
    
    if success_global and success_account:
        # Get updated trade details for confirmation
        all_trades = storage.read_all_trades(global_csv_path)
        trade = next((t for t in all_trades if int(t['trade_id']) == trade_id), None)
        
        result_display = status_rule.format_result_display(result)
        status_display = status_rule.format_status_display(new_status)
        
        await query.edit_message_text(
            f"✅ <b>Trade Updated Successfully!</b>\n\n"
            f"🆔 Trade ID: <b>#{trade_id}</b>\n"
            f"💱 Pair: <b>{trade['pair']}</b>\n"
            f"📊 Direction: <b>{trade['direction']}</b>\n"
            f"💰 Entry: <b>{trade['entry']}</b>\n\n"
            f"📈 Status: <b>{status_display}</b>\n"
            f"🎯 Result: <b>{result_display}</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💡 Use /opentrades to view remaining open trades\n"
            "📜 Use /recenttrades to see all recent trades",
            parse_mode='HTML'
        )
    else:
        await query.edit_message_text(
            "❌ <b>Error updating trade!</b>\n\n"
            "Please try again with /updatetrade",
            parse_mode='HTML'
        )
    
    # Clear user data
    context.user_data.clear()
    return ConversationHandler.END


async def cancel_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the update conversation."""
    await update.message.reply_html(
        "❌ <b>Update cancelled.</b>\n\n"
        "Use /updatetrade when you're ready."
    )
    context.user_data.clear()
    return ConversationHandler.END
