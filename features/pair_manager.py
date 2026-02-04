"""
Pair Manager - Handle user's favorite trading pairs
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from features import user_manager


# Conversation states
SELECT_ACTION, ADD_PAIR, DELETE_PAIR = range(3)


async def manage_pairs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show pair management menu."""
    user_id = update.effective_user.id
    pairs = user_manager.get_user_pairs(user_id)
    
    # Create pair buttons in rows of 3
    pair_buttons = []
    for i in range(0, len(pairs), 3):
        row = [InlineKeyboardButton(f"❌ {pair}", callback_data=f"delete_pair_{pair}") 
               for pair in pairs[i:i+3]]
        pair_buttons.append(row)
    
    # Add action buttons
    pair_buttons.append([InlineKeyboardButton("➕ Add New Pair", callback_data="add_pair")])
    pair_buttons.append([InlineKeyboardButton("✅ Done", callback_data="done_pairs")])
    
    keyboard = InlineKeyboardMarkup(pair_buttons)
    
    message_text = (
        "⚙️ <b>Manage Your Trading Pairs</b>\n\n"
        f"📊 <b>Your Pairs ({len(pairs)}):</b>\n"
    )
    
    for pair in pairs:
        message_text += f"• {pair}\n"
    
    message_text += "\n💡 <i>Tap ❌ to delete a pair, or add new ones</i>"
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    else:
        await update.message.reply_html(message_text, reply_markup=keyboard)
    
    return SELECT_ACTION


async def handle_pair_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle pair management actions."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    if data == "add_pair":
        await query.message.edit_text(
            "➕ <b>Add New Trading Pair</b>\n\n"
            "Enter the pair symbol (e.g., EURUSD, XAUUSD, BTCUSDT)\n\n"
            "💡 <i>Or send /cancel to go back</i>",
            parse_mode='HTML'
        )
        return ADD_PAIR
    
    elif data.startswith("delete_pair_"):
        pair = data.replace("delete_pair_", "")
        success = user_manager.remove_user_pair(user_id, pair)
        
        if success:
            await query.message.edit_text(
                f"✅ <b>Deleted: {pair}</b>\n\n"
                "Redirecting...",
                parse_mode='HTML'
            )
        else:
            await query.message.edit_text(
                f"❌ <b>Error deleting {pair}</b>\n\n"
                "Redirecting...",
                parse_mode='HTML'
            )
        
        # Show updated menu
        import asyncio
        await asyncio.sleep(1)
        return await manage_pairs(update, context)
    
    elif data == "done_pairs":
        await query.message.edit_text(
            "✅ <b>Pair Management Complete!</b>\n\n"
            "Your pairs have been saved.",
            parse_mode='HTML'
        )
        return ConversationHandler.END
    
    return SELECT_ACTION


async def receive_new_pair(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and add new pair."""
    user_id = update.effective_user.id
    pair = update.message.text.strip().upper()
    
    # Basic validation
    if len(pair) < 4 or len(pair) > 10:
        await update.message.reply_html(
            "❌ <b>Invalid pair format</b>\n\n"
            "Please enter a valid pair symbol (4-10 characters)\n"
            "Example: EURUSD, XAUUSD, BTCUSDT"
        )
        return ADD_PAIR
    
    success = user_manager.add_user_pair(user_id, pair)
    
    if success:
        await update.message.reply_html(
            f"✅ <b>Added: {pair}</b>\n\n"
            "Showing updated list..."
        )
    else:
        await update.message.reply_html(
            f"⚠️ <b>{pair} already exists!</b>\n\n"
            "Showing your pairs..."
        )
    
    # Show updated menu
    return await manage_pairs(update, context)


async def cancel_pair_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel pair management."""
    await update.message.reply_html(
        "❌ <b>Cancelled</b>\n\n"
        "Pair management cancelled."
    )
    return ConversationHandler.END
