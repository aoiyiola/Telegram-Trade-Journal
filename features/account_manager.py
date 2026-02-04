"""
Account Manager - Handle user's trading accounts
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from features import user_manager


# Conversation states
SELECT_ACCOUNT_ACTION, ADD_ACCOUNT, RENAME_ACCOUNT, SELECT_ACCOUNT_TO_RENAME, SELECT_ACCOUNT_TO_DELETE = range(5)


async def manage_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show account management menu."""
    user_id = update.effective_user.id
    accounts = user_manager.get_user_accounts(user_id)
    default_account = user_manager.get_default_account(user_id)
    default_id = default_account['id'] if default_account else None
    
    # Create account buttons
    account_buttons = []
    for account in accounts:
        is_default = "⭐ " if account['id'] == default_id else ""
        button_text = f"{is_default}{account['name']}"
        account_buttons.append([
            InlineKeyboardButton(button_text, callback_data=f"view_acc_{account['id']}")
        ])
    
    # Add action buttons
    account_buttons.append([InlineKeyboardButton("➕ Add Account", callback_data="add_account")])
    account_buttons.append([InlineKeyboardButton("✅ Done", callback_data="done_accounts")])
    
    keyboard = InlineKeyboardMarkup(account_buttons)
    
    message_text = (
        "⚙️ <b>Manage Your Trading Accounts</b>\n\n"
        f"📊 <b>Your Accounts ({len(accounts)}/3 max):</b>\n\n"
    )
    
    for account in accounts:
        default_marker = "⭐ " if account['id'] == default_id else "  "
        message_text += f"{default_marker}<b>{account['name']}</b>\n"
        message_text += f"   ID: <code>{account['id']}</code>\n\n"
    
    message_text += "💡 <i>⭐ = Default account</i>\n"
    message_text += "💡 <i>Tap an account to manage it</i>"
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    else:
        await update.message.reply_html(message_text, reply_markup=keyboard)
    
    return SELECT_ACCOUNT_ACTION


async def view_account_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show individual account management options."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    account_id = query.data.replace("view_acc_", "")
    
    account = user_manager.get_account_by_id(user_id, account_id)
    if not account:
        await query.message.edit_text("❌ Account not found")
        return ConversationHandler.END
    
    default_account = user_manager.get_default_account(user_id)
    is_default = default_account and default_account['id'] == account_id
    
    # Create action buttons
    buttons = []
    
    if not is_default:
        buttons.append([InlineKeyboardButton("⭐ Set as Default", callback_data=f"set_default_{account_id}")])
    
    buttons.append([InlineKeyboardButton("✏️ Rename", callback_data=f"rename_acc_{account_id}")])
    
    accounts = user_manager.get_user_accounts(user_id)
    if len(accounts) > 1:  # Don't allow deleting last account
        buttons.append([InlineKeyboardButton("❌ Delete", callback_data=f"delete_acc_{account_id}")])
    
    buttons.append([InlineKeyboardButton("« Back", callback_data="back_to_accounts")])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    default_text = "⭐ <b>DEFAULT</b>\n" if is_default else ""
    
    message_text = (
        f"📊 <b>Account Details</b>\n\n"
        f"{default_text}"
        f"<b>Name:</b> {account['name']}\n"
        f"<b>ID:</b> <code>{account['id']}</code>\n"
        f"<b>CSV:</b> <code>{account['csv_path']}</code>\n\n"
        "What would you like to do?"
    )
    
    await query.message.edit_text(message_text, reply_markup=keyboard, parse_mode='HTML')
    return SELECT_ACCOUNT_ACTION


async def handle_account_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle account management actions."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    if data == "add_account":
        # Check account limit (max 3 accounts)
        accounts = user_manager.get_user_accounts(user_id)
        if len(accounts) >= 3:
            await query.message.edit_text(
                "❌ <b>Account Limit Reached</b>\n\n"
                "You can have a maximum of <b>3 trading accounts</b>.\n\n"
                "💡 Delete an existing account to create a new one.\n\n"
                "Tap the button below to go back.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="back_to_accounts")]]),
                parse_mode='HTML'
            )
            return SELECT_ACCOUNT_ACTION
        
        await query.message.edit_text(
            "➕ <b>Add New Trading Account</b>\n\n"
            "Enter a name for this account\n"
            "Examples: Demo Account, Live Account, Test\n\n"
            "💡 <i>Or send /cancel to go back</i>",
            parse_mode='HTML'
        )
        return ADD_ACCOUNT
    
    elif data.startswith("set_default_"):
        account_id = data.replace("set_default_", "")
        success = user_manager.set_default_account(user_id, account_id)
        
        if success:
            await query.message.edit_text(
                "✅ <b>Default account updated!</b>\n\n"
                "Redirecting...",
                parse_mode='HTML'
            )
        else:
            await query.message.edit_text(
                "❌ <b>Error updating default account</b>",
                parse_mode='HTML'
            )
        
        import asyncio
        await asyncio.sleep(1)
        return await manage_accounts(update, context)
    
    elif data.startswith("rename_acc_"):
        account_id = data.replace("rename_acc_", "")
        context.user_data['account_to_rename'] = account_id
        
        await query.message.edit_text(
            "✏️ <b>Rename Account</b>\n\n"
            "Enter the new name for this account\n\n"
            "💡 <i>Or send /cancel to go back</i>",
            parse_mode='HTML'
        )
        return RENAME_ACCOUNT
    
    elif data.startswith("delete_acc_"):
        account_id = data.replace("delete_acc_", "")
        success = user_manager.remove_user_account(user_id, account_id)
        
        if success:
            await query.message.edit_text(
                "✅ <b>Account deleted!</b>\n\n"
                "Redirecting...",
                parse_mode='HTML'
            )
        else:
            await query.message.edit_text(
                "❌ <b>Cannot delete account</b>\n"
                "You must have at least one account.",
                parse_mode='HTML'
            )
        
        import asyncio
        await asyncio.sleep(1)
        return await manage_accounts(update, context)
    
    elif data == "back_to_accounts":
        return await manage_accounts(update, context)
    
    elif data == "done_accounts":
        await query.message.edit_text(
            "✅ <b>Account Management Complete!</b>\n\n"
            "Your accounts have been saved.",
            parse_mode='HTML'
        )
        return ConversationHandler.END
    
    return SELECT_ACCOUNT_ACTION


async def receive_new_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and create new account."""
    user_id = update.effective_user.id
    account_name = update.message.text.strip()
    
    if len(account_name) < 2 or len(account_name) > 50:
        await update.message.reply_html(
            "❌ <b>Invalid account name</b>\n\n"
            "Please enter a name between 2-50 characters"
        )
        return ADD_ACCOUNT
    
    account = user_manager.add_user_account(user_id, account_name)
    
    await update.message.reply_html(
        f"✅ <b>Created: {account_name}</b>\n"
        f"<b>ID:</b> <code>{account['id']}</code>\n\n"
        "Showing updated list..."
    )
    
    return await manage_accounts(update, context)


async def receive_account_rename(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and apply new account name."""
    user_id = update.effective_user.id
    new_name = update.message.text.strip()
    account_id = context.user_data.get('account_to_rename')
    
    if not account_id:
        await update.message.reply_html("❌ <b>Error: No account selected</b>")
        return ConversationHandler.END
    
    if len(new_name) < 2 or len(new_name) > 50:
        await update.message.reply_html(
            "❌ <b>Invalid account name</b>\n\n"
            "Please enter a name between 2-50 characters"
        )
        return RENAME_ACCOUNT
    
    success = user_manager.rename_user_account(user_id, account_id, new_name)
    
    if success:
        await update.message.reply_html(
            f"✅ <b>Account renamed to: {new_name}</b>\n\n"
            "Showing updated list..."
        )
    else:
        await update.message.reply_html(
            "❌ <b>Error renaming account</b>"
        )
    
    context.user_data.pop('account_to_rename', None)
    return await manage_accounts(update, context)


async def cancel_account_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel account management."""
    await update.message.reply_html(
        "❌ <b>Cancelled</b>\n\n"
        "Account management cancelled."
    )
    context.user_data.pop('account_to_rename', None)
    return ConversationHandler.END
