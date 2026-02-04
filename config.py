"""
Configuration settings for the Trading Journal Bot
"""
import os
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Timezone
TIMEZONE = pytz.timezone('Europe/London')

# Trading Sessions (UK time)
# Note: All hours belong to one of these three sessions
SESSIONS = {
    'Asia': (0, 6),      # 00:00 - 06:59
    'London': (7, 12),   # 07:00 - 12:59
    'New York': (13, 23), # 13:00 - 23:59 (includes all remaining hours)
}

# News Risk Settings
NEWS_RISK_WINDOW_MINUTES = 10  # ±10 minutes around high-impact news
FCS_API_KEY = os.getenv('FCS_API_KEY', '')  # Get free key from fcsapi.com

# CSV File Path
TRADES_CSV_PATH = 'data/trades.csv'
NEWS_CACHE_PATH = 'data/news_cache.json'
USER_REGISTRY_PATH = 'data/users_registry.csv'  # Admin-only user registration data
DATA_DIR = 'data'
