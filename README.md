# TRADING JOURNAL TELEGRAM BOT

## Project Overview
A Telegram-based trading journal bot designed to log, manage, and review trades in a structured, rule-based, and automated way. The bot focuses on discipline and data collection rather than prediction. All logic is deterministic (no AI).

## Key Features

### 1. Trade Logging
- **Guided Input:** Step-by-step prompts for Pair, Direction, Entry, SL, TP, and Notes.
- **Auto-Save:** Trades are automatically saved to CSV with a default status of `OPEN`.

### 2. Automatic Session Tagging
- **Time-Based:** Sessions are detected automatically based on UK time.
- **Schedules:**
  - **Asia:** 00:00 – 06:59
  - **London:** 07:00 – 12:59
  - **New York:** 13:00 – 21:00
  - **Off:** Outside defined hours

### 3. News Risk Management
- **API Integration:** Detects high-impact economic news via Investing.com or ForexFactory.
- **Risk Flagging:** Trades executed within a specific time window of high-impact news are flagged as `HIGH` risk.
- **Caching:** News data is cached daily to optimize API usage.

### 4. Status & Rules
- **Statuses:** `OPEN`, `CLOSED`, `BREAKEVEN`, `VIOLATION`.
- **Logic:** Status updates automatically based on trade results (W/L/DD).

### 5. Queries & Updates
- **Query:** List open trades or recent activity.
- **Update:** Modify trade results (Win/Loss/Drawdown) seamlessly.

## Project Structure

This project follows a modular feature design:

```text
trading_journal_bot/
│
├── bot.py              # Telegram bot entry point
├── core.py             # Routing + conversation state handling
├── config.py           # Timezone, sessions, API keys, rule settings
│
├── features/
│   ├── trade_logger.py   # New trade conversation + save logic
│   ├── session_tag.py    # Auto session detection (time-based)
│   ├── news_rule.py      # News risk detection (API + cache)
│   ├── status_rule.py    # Status assignment and rule logic
│   ├── trade_query.py    # List and filter trades
│   └── trade_update.py   # Update trade results
│
├── storage.py          # CSV read/write operations
├── formatters.py       # User-facing message formatting
├── utils.py            # Time helpers, ID generation
│
├── data/
│   ├── trades.csv
│   └── news_cache.json
│
└── # Trading Journal Telegram Bot

A Telegram-based trading journal bot for logging, managing, and reviewing trades with automated session tagging and news risk detection.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a Telegram Bot:**
   - Talk to [@BotFather](https://t.me/BotFather) on Telegram
   - Use `/newbot` command and follow instructions
   - Copy your bot token

3. **Configure environment:**
   ```bash
   cp .env.example .env
   ```
   - Edit `.env` and add your bot token

4. **Run the bot:**
   ```bash
   python bot.py
   ```

5. **Test it:**
   - Find your bot on Telegram
   - Send `/start` command
   - You should see a welcome message!

## Current Status

✅ Bot connection and basic commands
🚧 Feature modules (in development)

## Project Structure

See `trading_journal_project_schema.txt` for detailed project overview and planned features.
