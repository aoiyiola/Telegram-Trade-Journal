"""
Trade logger module - Guided conversation for logging new trades
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
import storage
import utils
from features import session_tag, status_rule, news_rule, user_manager


# Conversation states
SELECT_ACCOUNT, SELECT_PAIR, DIRECTION, ENTRY, STOP_LOSS, TAKE_PROFIT, NOTES = range(7)


async def start_new_trade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the trade logging conversation - Select account first."""
    user_id = update.effective_user.id
    accounts = user_manager.get_user_accounts(user_id)
    default_account = user_manager.get_default_account(user_id)
    
    # Create account selection buttons
    account_buttons = []
    for account in accounts:
        is_default = "⭐ " if default_account and account['id'] == default_account['id'] else ""
        button_text = f"{is_default}{account['name']}"
        account_buttons.append([InlineKeyboardButton(button_text, callback_data=f"select_acc_{account['id']}")])
    
    keyboard = InlineKeyboardMarkup(account_buttons)
    
    await update.message.reply_html(
        "📝 <b>New Trade Entry</b>\n\n"
        "Let's log your trade step by step.\n\n"
        "📊 <b>Step 1/7:</b> Select Trading Account\n\n"
        "💡 Send /cancel to abort",
        reply_markup=keyboard
    )
    return SELECT_ACCOUNT


async def receive_account_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive account selection and show pair selection."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    account_id = query.data.replace("select_acc_", "")
    
    account = user_manager.get_account_by_id(user_id, account_id)
    if not account:
        await query.message.edit_text("❌ Account not found")
        return ConversationHandler.END
    
    context.user_data['account'] = account
    
    # Get user's pairs
    pairs = user_manager.get_user_pairs(user_id)
    
    # Create pair buttons in rows of 3
    pair_buttons = []
    for i in range(0, len(pairs), 3):
        row = [InlineKeyboardButton(pair, callback_data=f"select_pair_{pair}") 
               for pair in pairs[i:i+3]]
        pair_buttons.append(row)
    
    keyboard = InlineKeyboardMarkup(pair_buttons)
    
    await query.edit_message_text(
        f"✅ Account: <b>{account['name']}</b>\n\n"
        f"💱 <b>Step 2/7:</b> Select Trading Pair\n\n"
        "💡 <i>Manage pairs with /managepairs</i>",
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    return SELECT_PAIR


async def receive_pair_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive pair selection and show direction buttons."""
    query = update.callback_query
    await query.answer()
    
    pair = query.data.replace("select_pair_", "")
    context.user_data['pair'] = pair
    account = context.user_data['account']
    
    # Create inline keyboard for direction
    keyboard = [
        [
            InlineKeyboardButton("📈 BUY", callback_data="direction_BUY"),
            InlineKeyboardButton("📉 SELL", callback_data="direction_SELL")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ Account: <b>{account['name']}</b>\n"
        f"✅ Pair: <b>{pair}</b>\n\n"
        "📊 <b>Step 3/7:</b> What's the direction?\n\n"
        "Tap a button below:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    return DIRECTION


async def receive_direction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and validate the direction from button click."""
    query = update.callback_query
    await query.answer()
    
    # Extract direction from callback data
    direction = query.data.split('_')[1]  # "direction_BUY" -> "BUY"
    context.user_data['direction'] = direction
    pair = context.user_data['pair']
    account = context.user_data['account']
    
    # Edit the message to show selection
    await query.edit_message_text(
        f"✅ Account: <b>{account['name']}</b>\n"
        f"✅ Pair: <b>{pair}</b>\n"
        f"✅ Direction: <b>{direction}</b>",
        parse_mode='HTML'
    )
    
    # Send next prompt
    await query.message.reply_html(
        "💰 <b>Step 4/7:</b> What's your entry price?\n"
        f"<i>Example for {pair}: 1.0850</i>"
    )
    return ENTRY


async def receive_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and validate the entry price."""
    try:
        entry = float(update.message.text.strip())
        context.user_data['entry'] = entry
        
        await update.message.reply_html(
            f"✅ Entry: <b>{entry}</b>\n\n"
            "🛑 <b>Step 5/7:</b> What's your stop loss?\n"
            "<i>Enter the SL price</i>"
        )
        return STOP_LOSS
    except ValueError:
        await update.message.reply_html(
            "❌ Invalid price format.\n\n"
            "Please enter a valid number.\n"
            "<i>Example: 1.0850</i>"
        )
        return ENTRY


async def receive_stop_loss(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and validate the stop loss."""
    try:
        sl = float(update.message.text.strip())
        context.user_data['sl'] = sl
        
        await update.message.reply_html(
            f"✅ Stop Loss: <b>{sl}</b>\n\n"
            "🎯 <b>Step 6/7:</b> What's your take profit?\n"
            "<i>Enter the TP price</i>"
        )
        return TAKE_PROFIT
    except ValueError:
        await update.message.reply_html(
            "❌ Invalid price format.\n\n"
            "Please enter a valid number.\n"
            "<i>Example: 1.0830</i>"
        )
        return STOP_LOSS


async def receive_take_profit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and validate the take profit."""
    try:
        tp = float(update.message.text.strip())
        context.user_data['tp'] = tp
        
        # Create inline keyboard for notes option
        keyboard = [
            [InlineKeyboardButton("➖ Skip Notes", callback_data="notes_skip")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_html(
            f"✅ Take Profit: <b>{tp}</b>\n\n"
            "📝 <b>Step 7/7:</b> Any notes for this trade?\n"
            "<i>Optional - describe your setup, strategy, etc.</i>\n\n"
            "💡 Type your notes or tap Skip Notes below:",
            reply_markup=reply_markup
        )
        return NOTES
    except ValueError:
        await update.message.reply_html(
            "❌ Invalid price format.\n\n"
            "Please enter a valid number.\n"
            "<i>Example: 1.0890</i>"
        )
        return TAKE_PROFIT


async def receive_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive notes and save the complete trade."""
    # Check if it's a callback (skip button) or text message
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        notes = ''
        # Edit the message to show skipped
        await query.edit_message_text(
            f"✅ Take Profit: <b>{context.user_data['tp']}</b>\n"
            "📝 Notes: <i>Skipped</i>",
            parse_mode='HTML'
        )
        message_to_reply = query.message
    else:
        notes = update.message.text.strip()
        if notes == '-':
            notes = ''
        message_to_reply = update.message
    
    # Get all trade data
    account = context.user_data['account']
    pair = context.user_data['pair']
    direction = context.user_data['direction']
    entry = context.user_data['entry']
    sl = context.user_data['sl']
    tp = context.user_data['tp']
    
    # Auto-generate data
    telegram_id = update.effective_user.id
    trade_id = storage.get_next_trade_id(telegram_id)
    
    datetime_str = utils.get_current_datetime_string()
    trade_datetime = utils.get_current_uk_time()
    session = session_tag.get_session()
    status = 'OPEN'
    news_risk = news_rule.check_news_risk(trade_datetime)
    result = ''
    
    # Create trade data
    trade_data = {
        'trade_id': trade_id,
        'account_id': account['id'],
        'datetime': datetime_str,
        'pair': pair,
        'direction': direction,
        'entry': entry,
        'sl': sl,
        'tp': tp,
        'session': session,
        'status': status,
        'news_risk': news_risk,
        'result': result,
        'notes': notes
    }
    
    # Save to database
    success = storage.save_trade(trade_data, telegram_id)
    
    if success:
        # Format confirmation message
        session_display = session_tag.format_session_display(session)
        status_display = status_rule.format_status_display(status)
        
        message = (
            "✅ <b>Trade Logged Successfully!</b>\n\n"
            f"📊 Account: <b>{account['name']}</b>\n"
            f"🆔 Trade ID: <b>#{trade_id}</b>\n"
            f"📅 Time: <b>{utils.format_display_datetime(datetime_str)}</b>\n"
            f"🌍 Session: <b>{session_display}</b>\n\n"
            f"💱 Pair: <b>{pair}</b>\n"
            f"📊 Direction: <b>{direction}</b>\n"
            f"💰 Entry: <b>{entry}</b>\n"
            f"🛑 Stop Loss: <b>{sl}</b>\n"
            f"🎯 Take Profit: <b>{tp}</b>\n\n"
            f"📈 Status: <b>{status_display}</b>\n"
            f"📰 News Risk: <b>{'⚠️' if news_risk == 'HIGH' else '✅'} {news_risk}</b>\n"
        )
        
        if notes:
            message += f"\n📝 Notes: <i>{notes}</i>\n"
        
        message += (
            "\n" + "="*25 + "\n"
            "💡 Use /opentrades to view all open trades\n"
            "✏️ Use /updatetrade to update the result later"
        )
        
        await message_to_reply.reply_html(message)
    else:
        await message_to_reply.reply_html(
            "❌ <b>Error saving trade!</b>\n\n"
            "Please try again with /newtrade"
        )
    
    # Clear user data
    context.user_data.clear()
    return ConversationHandler.END


async def cancel_trade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the trade logging conversation."""
    await update.message.reply_html(
        "❌ <b>Trade logging cancelled.</b>\n\n"
        "Use /newtrade when you're ready to log a trade."
    )
    context.user_data.clear()
    return ConversationHandler.END
