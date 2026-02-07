"""
Startup script - Runs both the Telegram bot and web dashboard server
"""
import os
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
    logger.info(f"🌐 Starting web server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)


def main():
    """Start both bot and web server."""
    logger.info("🚀 Starting Trading Journal Bot & Dashboard")
    
    # Start web server in background thread
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    logger.info("✅ Web server thread started")
    
    # Start Telegram bot (this blocks)
    logger.info("🤖 Starting Telegram bot...")
    bot.main()


if __name__ == '__main__':
    main()
