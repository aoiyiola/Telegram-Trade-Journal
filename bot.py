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
import database
from features import trade_logger, trade_query, trade_update, news_rule, admin_commands, pair_manager, account_manager, user_manager

# Initialize database on startup
try:
    database.init_database()
    print("✅ Database initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize database: {e}")
    print(f"⚠️ Please make sure DATABASE_URL is set in environment variables")

# Initialize news cache on startup
try:
    news_rule.init_sample_news()
    print("✅ News cache initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize news cache: {e}")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Reduce APScheduler noise - only show warnings and errors
logging.getLogger('apscheduler').setLevel(logging.WARNING)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    user_id = user.id
    
    # Subscribe user to news alerts
    if 'subscribed_users' not in context.bot_data:
        context.bot_data['subscribed_users'] = set()
    context.bot_data['subscribed_users'].add(chat_id)
    
    # Check if user is already registered in the registry (more reliable than config file)
    user_exists = user_manager.user_exists_in_registry(user_id)
    
    # Check if config file exists
    config_path = user_manager.get_user_config_path(user_id)
    config_exists = os.path.exists(config_path)
    
    # User is new ONLY if they're not in registry AND no config exists
    is_new_user = not user_exists and not config_exists
    
    if is_new_user:
        # New user - ask for email first
        welcome_message = (
            f"👋 <b>Welcome {user.mention_html()}!</b>\n\n"
            "📊 <b>Trading Journal Bot</b>\n"
            "Your personal trading assistant for disciplined trade management.\n\n"
            "🎯 Let's get you set up! First, please provide your email address.\n\n"
            "📧 <b>Why we need your email:</b>\n"
            "• Account recovery and security\n"
            "• Important trade notifications\n"
            "• Weekly performance reports\n\n"
            "Please provide me your email address:\n"
            "Example: <i>yourname@example.com</i>\n\n"
        
        )
        # Store state for conversation
        context.user_data['awaiting_email'] = True
    else:
        # Existing user - show regular welcome
        # If config missing but user exists in registry, recreate default config
        if not config_exists:
            print(f"⚠️ Config missing for user {user_id} but exists in registry - recreating default config")
            user_manager.load_user_config(user_id)  # This creates default config
        
        # Ensure existing user is registered in the registry (for users who joined before registry feature)
        user_config = user_manager.load_user_config(user_id)
        user_email = user_config.get('email')
        
        user_manager.register_user(
            telegram_id=user_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user_email
        )
        
        # Show full command menu to registered user
        await set_user_commands(context.application, chat_id)
        
        welcome_message = (
            f"👋 <b>Hi {user.mention_html()}!</b>\n\n"
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
        "/news - 📰 View today's news\n"
        "/help - 📚 Get detailed help\n\n"
        "💡 <i>Tap any command to use it!</i>\n"
        "🔔 You'll receive news alerts automatically\n"
        "🚀 Ready to maintain your trading discipline!"
    )
    await update.message.reply_html(welcome_message)


async def handle_setup_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle first-time email setup."""
    if not context.user_data.get('awaiting_email'):
        return
    
    user_id = update.effective_user.id
    message_text = update.message.text.strip()
    
    # Handle skip
    if message_text == '/skip':
        user_email = None
    else:
        # Validate email format (basic check)
        if '@' not in message_text or '.' not in message_text.split('@')[-1]:
            await update.message.reply_html(
                "❌ Invalid email format.\n"
                "Please provide a valid email address or /skip to skip."
            )
            return
        user_email = message_text.lower()
    
    # Store email in user_data for next step
    context.user_data['user_email'] = user_email
    context.user_data.pop('awaiting_email', None)
    
    # Now ask for account name
    if user_email:
        message = (
            f"✅ <b>Email saved:</b> {user_email}\n\n"
            "🎯 Now, let's name your main trading account.\n\n"
            "Please send me the name for your main account:\n"
            "Example: <i>Live Account</i>, <i>Demo</i>, <i>Prop Firm</i>\n\n"
            "Or type <b>/skip</b> to use default name <b>'Main Account'</b>"
        )
    else:
        message = (
            "⚠️ <b>Email skipped</b>\n\n"
            "🎯 Now, let's name your main trading account.\n\n"
            "Please send me the name for your main account:\n"
            "Example: <i>Live Account</i>, <i>Demo</i>, <i>Prop Firm</i>\n\n"
            "Or type <b>/skip</b> to use default name <b>'Main Account'</b>"
        )
    
    context.user_data['awaiting_account_name'] = True
    await update.message.reply_html(message)


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
    
    # Create user config with custom account name and email
    user_dir = user_manager.get_user_data_dir(user_id)
    user_email = context.user_data.get('user_email')
    
    default_config = {
        'user_id': user_id,
        'email': user_email,
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
    
    # Register user in the admin registry CSV (checks for duplicates automatically)
    user = update.effective_user
    user_manager.register_user(
        telegram_id=user_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user_email
    )
    
    # Clear state
    context.user_data.pop('awaiting_account_name', None)
    context.user_data.pop('user_email', None)
    
    # Show full command menu to newly registered user
    await set_user_commands(context.application, update.effective_chat.id)
    
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
        "/news - 📰 View today's news\n"
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
        "/news - 📰 View today's news\n"
        "/addnews - ➕ Add news event manually\n"
        "/help - 📚 This help guide\n\n"
        "💡 <i>Tip: Tap any command to use it instantly!</i>"
    )
    await update.message.reply_html(help_text)


async def post_init(application: Application) -> None:
    """Set bot commands in the menu after initialization."""
    # Default commands (only start for new users)
    default_commands = [
        BotCommand("start", "🏠 Start the bot"),
    ]
    await application.bot.set_my_commands(default_commands)
    logger.info("✅ Bot commands menu set (default)")


async def set_user_commands(application: Application, telegram_id: int) -> None:
    """Set full command menu for registered users."""
    full_commands = [
        BotCommand("start", "🏠 Welcome screen"),
        BotCommand("newtrade", "📝 Log a new trade"),
        BotCommand("managepairs", "💱 Manage trading pairs"),
        BotCommand("manageaccounts", "📊 Manage accounts"),
        BotCommand("opentrades", "📊 View open trades"),
        BotCommand("recenttrades", "📜 View recent trades"),
        BotCommand("updatetrade", "✏️ Update trade result"),
        BotCommand("news", "📰 View today's news"),
        BotCommand("addnews", "➕ Add news event manually"),
        BotCommand("help", "📚 Help guide"),
    ]
    try:
        # Set commands for this specific user
        from telegram import BotCommandScopeChat
        await application.bot.set_my_commands(
            full_commands,
            scope=BotCommandScopeChat(chat_id=telegram_id)
        )
        logger.info(f"✅ Full commands set for user {telegram_id}")
    except Exception as e:
        logger.error(f"❌ Error setting commands for user: {e}")


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
    
    # Message handler for first-time user setup (email and account - in group 1, after all conversation handlers)
    async def handle_first_time_setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Route first-time setup messages to appropriate handler."""
        if context.user_data.get('awaiting_email'):
            await handle_setup_email(update, context)
        elif context.user_data.get('awaiting_account_name'):
            await handle_setup_account_name(update, context)
    
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
            handle_first_time_setup
        ),
        group=1  # Lower priority than conversation handlers
    )
    
    # Set up news refresh job - every 4 hours (6 times per day)
    application.job_queue.run_repeating(
        admin_commands.refresh_news_cache_job,
        interval=14400,  # 4 hours = 14400 seconds
        first=60,  # Start 60 seconds after bot starts
        name='news_refresh'
    )
    
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
    logger.info("� News cache auto-refreshes every 4 hours (6 times/day)")
    logger.info("📰 Daily news summary scheduled for 00:05 UK time")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
