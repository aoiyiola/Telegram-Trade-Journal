"""
Startup script - Runs both the Telegram bot and web dashboard server
"""
import os
import sys
import threading
import logging
from web_server import app
import bot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def run_web_server():
    """Run Flask web server in a separate thread."""
    port = int(os.getenv('PORT', 8080))
    logger.info(f"Starting web server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)


def run_bot():
    """Run Telegram bot in foreground."""
    logger.info("Starting Telegram bot")
    bot.main()


def resolve_start_mode() -> str:
    """Resolve run mode from CLI arg first, then START_MODE env var."""
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return sys.argv[1].strip().lower()
    return os.getenv('START_MODE', 'both').strip().lower()


def main():
    """Start app based on mode: web, bot, or both."""
    mode = resolve_start_mode()

    if mode == 'web':
        logger.info("START_MODE=web")
        run_web_server()
        return

    if mode == 'bot':
        logger.info("START_MODE=bot")
        run_bot()
        return

    if mode != 'both':
        logger.warning(f"Unknown START_MODE '{mode}', defaulting to 'both'")

    logger.info("START_MODE=both")

    # Start web server in background thread so the process binds to PORT.
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    logger.info("Web server thread started")

    # Run bot in foreground (blocking)
    run_bot()


if __name__ == '__main__':
    main()
