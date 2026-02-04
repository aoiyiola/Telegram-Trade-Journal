"""
Trading Journal Telegram Bot - Entry Point
"""
import logging
import datetime
import os
from telegram import Update, BotCommand
from telegram.ext import (
    Application, 
    CommandHandler, 
    ConversationHandler, 
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
import config
from features import trade_logger, trade_query, trade_update, news_rule, admin_commands, pair_manager, account_manager, user_manager

# Initialize news cache on startup
news_rule.init_sample_news()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    user_id = user.id
    
    # Subscribe user to news alerts
    if 'subscribed_users' not in context.bot_data:
        context.bot_data['subscribed_users'] = set()
    context.bot_data['subscribed_users'].add(chat_id)
    
    # Check if this is first time user (no config exists)
    config_path = user_manager.get_user_config_path(user_id)
    is_new_user = not os.path.exists(config_path)
    
    if is_new_user:
        # New user - ask for main account name
        welcome_message = (
            f"👋 <b>Welcome {user.mention_html()}!</b>\n\n"
            "📊 <b>Trading Journal Bot</b>\n"
            "Your personal trading assistant for disciplined trade management.\n\n"
            "🎯 Let's get started! First, let's name your main trading account.\n\n"
            "Please send me the name for your main account:\n"
            "Example: <i>Live Account</i>, <i>Demo</i>, <i>Prop Firm</i>\n\n"
            "Or type <b>/skip</b> to use default name <b>'Main Account'</b>"
        )
        # Store state for conversation
        context.user_data['awaiting_account_name'] = True
    else:
        # Existing user - show regular welcome
        welcome_message = (
            f"👋 <b>Welcome back {user.mention_html()}!</b>\n\n"
            "📊 <b>Trading Journal Bot</b>\n"
            "Your personal trading assistant for disciplined trade management.\n\n"
            "✨ <b>What I can do:</b>\n"
            "• 📝 Log trades to multiple accounts\n"
            "• 📊 Manage favorite trading pairs\n"
            "• 🌍 Auto-detect trading sessions (Asia/London/NY)\n"
            "• 📰 Flag high-impact news risk\n"
            "• ⚠️ Send alerts 10 min before news events\n"
            "• 📈 Track open and closed trades\n"
        "• 📊 Update trade results (W/L/BE)\n"
        "• 📊 Global & per-account CSV storage\n\n"
        "🎯 <b>Quick Commands:</b>\n"
        "/newtrade - 📝 Log a new trade\n"
        "/managepairs - 💱 Manage trading pairs\n"
        "/manageaccounts - 📊 Manage accounts\n"
        "/opentrades - 📊 View open trades\n"
        "/recenttrades - 📜 View recent trades\n"
        "/news - 📰 View upcoming news\n"
        "/help - 📚 Get detailed help\n\n"
        "💡 <i>Tap any command to use it!</i>\n"
        "🔔 You'll receive news alerts automatically\n"
        "🚀 Ready to maintain your trading discipline!"
    )
    await update.message.reply_html(welcome_message)


async def handle_setup_account_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle first-time account name setup."""
    if not context.user_data.get('awaiting_account_name'):
        return
    
    user_id = update.effective_user.id
    message_text = update.message.text.strip()
    
    # Handle skip
    if message_text == '/skip':
        account_name = 'Main Account'
    else:
        # Validate account name
        if len(message_text) < 2 or len(message_text) > 30:
            await update.message.reply_html(
                "❌ Account name must be between 2-30 characters.\n"
                "Please try again or /skip for default."
            )
            return
        account_name = message_text
    
    # Create user config with custom account name
    user_dir = user_manager.get_user_data_dir(user_id)
    default_config = {
        'user_id': user_id,
        'pairs': ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY'],
        'accounts': [
            {
                'id': 'main',
                'name': account_name,
                'csv_path': os.path.join(user_dir, 'account_main.csv')
            }
        ],
        'default_account': 'main'
    }
    user_manager.save_user_config(user_id, default_config)
    
    # Clear state
    context.user_data.pop('awaiting_account_name', None)
    
    # Send success message
    await update.message.reply_html(
        f"✅ <b>Setup Complete!</b>\n\n"
        f"🎯 Your account <b>'{account_name}'</b> has been created.\n\n"
        "✨ <b>What I can do:</b>\n"
        "• 📝 Log trades to multiple accounts\n"
        "• 📊 Manage favorite trading pairs\n"
        "• 🌍 Auto-detect trading sessions (Asia/London/NY)\n"
        "• 📰 Flag high-impact news risk\n"
        "• ⚠️ Send alerts 10 min before news events\n"
        "• 📈 Track open and closed trades\n"
        "• 📊 Update trade results (W/L/BE)\n"
        "• 📊 Global & per-account CSV storage\n\n"
        "🎯 <b>Quick Commands:</b>\n"
        "/newtrade - 📝 Log a new trade\n"
        "/managepairs - 💱 Manage trading pairs\n"
        "/manageaccounts - 📊 Manage accounts\n"
        "/opentrades - 📊 View open trades\n"
        "/recenttrades - 📜 View recent trades\n"
        "/news - 📰 View upcoming news\n"
        "/help - 📚 Get detailed help\n\n"
        "💡 <i>Ready to log your first trade!</i>\n"
        "🚀 Let's maintain your trading discipline!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "📚 <b>Trading Journal Bot - Help Guide</b>\n\n"
        "═══════════════════════════\n\n"
        "📝 <b>LOGGING TRADES</b>\n"
        "Use guided prompts to log your trades:\n"
        "• Select account (if you have multiple)\n"
        "• Choose pair from your favorites\n"
        "• Direction (BUY/SELL)\n"
        "• Entry, Stop Loss, Take Profit\n"
        "• Optional notes\n\n"
        "📊 <b>MULTI-ACCOUNT SUPPORT</b>\n"
        "• Each account has its own CSV file\n"
        "• All trades also logged to global CSV\n"
        "• Manage accounts with /manageaccounts\n"
        "• Set default account for quick access\n\n"
        "💱 <b>PAIR MANAGEMENT</b>\n"
        "• Save favorite trading pairs\n"
        "• Quick selection when logging trades\n"
        "• Add/remove pairs anytime\n"
        "• Use /managepairs to configure\n\n"
        "🌍 <b>SESSION AUTO-DETECTION</b>\n"
        "Sessions are tagged automatically (UK time):\n"
        "• 🌏 Asia: 00:00 - 06:59\n"
        "• 🇬🇧 London: 07:00 - 12:59\n"
        "• 🇺🇸 New York: 13:00 - 23:00\n\n"
        "📰 <b>NEWS RISK DETECTION</b>\n"
        "Trades near high-impact news are flagged:\n"
        "• ⚠️ HIGH - Within ±10 min of news\n"
        "• ✅ LOW - Safe timing\n\n"
        "📊 <b>TRADE STATUS</b>\n"
        "• 🟢 OPEN - Active trade\n"
        "• 🔴 CLOSED - Trade completed\n\n"
        "🎯 <b>TRADE RESULTS</b>\n"
        "• ✅ W - Win\n"
        "• ❌ L - Loss\n"
        "• ⚖️ BE - BreakEven\n\n"
        "🎯 <b>ALL COMMANDS</b>\n"
        "/start - 🏠 Welcome screen\n"
        "/newtrade - 📝 Log a new trade\n"
        "/managepairs - 💱 Manage trading pairs\n"
        "/manageaccounts - 📊 Manage accounts\n"
        "/opentrades - 📊 View open trades\n"
        "/recenttrades - 📜 View recent trades\n"
        "/updatetrade - ✏️ Update trade result\n"
        "/news - 📰 View upcoming news\n"
        "/refreshnews - 🔄 Refresh news cache\n"
        "/addnews - ➕ Add news event manually\n"
        "/help - 📚 This help guide\n\n"
        "💡 <i>Tip: Tap any command to use it instantly!</i>"
    )
    await update.message.reply_html(help_text)


async def post_init(application: Application) -> None:
    """Set bot commands in the menu after initialization."""
    commands = [
        BotCommand("start", "🏠 Welcome screen"),
        BotCommand("newtrade", "📝 Log a new trade"),
        BotCommand("managepairs", "💱 Manage trading pairs"),
        BotCommand("manageaccounts", "📊 Manage accounts"),
        BotCommand("opentrades", "📊 View open trades"),
        BotCommand("recenttrades", "📜 View recent trades"),
        BotCommand("updatetrade", "✏️ Update trade result"),
        BotCommand("news", "📰 View upcoming news"),
        BotCommand("refreshnews", "🔄 Refresh news cache"),
        BotCommand("addnews", "➕ Add news event manually"),
        BotCommand("help", "📚 Help guide"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("✅ Bot commands menu set")


def main() -> None:
    """Start the bot."""
    # Check if token is set
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found! Please set it in .env file")
        return
    
    # Create the Application with JobQueue
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("opentrades", trade_query.show_open_trades))
    application.add_handler(CommandHandler("recenttrades", trade_query.show_recent_trades))
    application.add_handler(CommandHandler("news", admin_commands.show_upcoming_news))
    application.add_handler(CommandHandler("refreshnews", admin_commands.refresh_news_command))
    application.add_handler(CommandHandler("addnews", admin_commands.add_news_event_command))
    
    # Pair management conversation handler
    pair_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("managepairs", pair_manager.manage_pairs)],
        states={
            pair_manager.SELECT_ACTION: [
                CallbackQueryHandler(pair_manager.handle_pair_action)
            ],
            pair_manager.ADD_PAIR: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, pair_manager.receive_new_pair)
            ],
        },
        fallbacks=[CommandHandler("cancel", pair_manager.cancel_pair_management)],
    )
    application.add_handler(pair_conv_handler)
    
    # Account management conversation handler
    account_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("manageaccounts", account_manager.manage_accounts)],
        states={
            account_manager.SELECT_ACCOUNT_ACTION: [
                CallbackQueryHandler(account_manager.handle_account_action),
                CallbackQueryHandler(account_manager.view_account_details, pattern="^view_acc_")
            ],
            account_manager.ADD_ACCOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, account_manager.receive_new_account)
            ],
            account_manager.RENAME_ACCOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, account_manager.receive_account_rename)
            ],
        },
        fallbacks=[CommandHandler("cancel", account_manager.cancel_account_management)],
    )
    application.add_handler(account_conv_handler)
    
    # Message handler for first-time account setup (must be before other message handlers)
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
            handle_setup_account_name
        )
    )
    
    # Trade logger conversation handler
    trade_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("newtrade", trade_logger.start_new_trade)],
        states={
            trade_logger.SELECT_ACCOUNT: [
                CallbackQueryHandler(trade_logger.receive_account_selection, pattern="^select_acc_")
            ],
            trade_logger.SELECT_PAIR: [
                CallbackQueryHandler(trade_logger.receive_pair_selection, pattern="^select_pair_")
            ],
            trade_logger.DIRECTION: [CallbackQueryHandler(trade_logger.receive_direction, pattern="^direction_")],
            trade_logger.ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, trade_logger.receive_entry)],
            trade_logger.STOP_LOSS: [MessageHandler(filters.TEXT & ~filters.COMMAND, trade_logger.receive_stop_loss)],
            trade_logger.TAKE_PROFIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, trade_logger.receive_take_profit)],
            trade_logger.NOTES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, trade_logger.receive_notes),
                CallbackQueryHandler(trade_logger.receive_notes, pattern="^notes_")
            ],
        },
        fallbacks=[CommandHandler("cancel", trade_logger.cancel_trade)],
    )
    application.add_handler(trade_conv_handler)
    
    # Trade update conversation handler
    update_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("updatetrade", trade_update.start_update_trade)],
        states={
            trade_update.SELECT_TRADE: [CallbackQueryHandler(trade_update.receive_trade_selection, pattern="^trade_")],
            trade_update.SELECT_RESULT: [CallbackQueryHandler(trade_update.receive_result, pattern="^result_")],
        },
        fallbacks=[CommandHandler("cancel", trade_update.cancel_update)],
        per_message=False
    )
    application.add_handler(update_conv_handler)
    
    # Set up news alert job - check every minute for upcoming news
    application.job_queue.run_repeating(
        admin_commands.send_news_alert,
        interval=60,  # Run every 60 seconds
        first=10,  # Start 10 seconds after bot starts
        name='news_alerts'
    )
    
    # Set up daily news refresh and summary - run at 00:05 UK time
    application.job_queue.run_daily(
        admin_commands.send_daily_news_summary,
        time=datetime.time(hour=0, minute=5),  # 00:05 UK time
        name='daily_news_summary'
    )

    # Start the Bot
    logger.info("🚀 Trading Journal Bot is starting...")
    logger.info("🔔 News alert system activated")
    logger.info("📰 Daily news refresh scheduled for 00:05 UK time")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
