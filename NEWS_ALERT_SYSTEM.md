# News Alert System - Documentation

## Overview
The Trading Journal Bot now includes an automated news alert system that:
- Fetches daily HIGH and MEDIUM impact news events
- Caches them locally for quick access
- Sends notifications 10 minutes before each news event
- Automatically refreshes news daily at 00:05 UK time

## Features

### 1. **Daily News Fetching**
- Fetches HIGH and MEDIUM impact news for today and tomorrow
- Stores events in `data/news_cache.json`
- Currently uses sample data (ForexFactory integration placeholder ready)
- Cleans old news automatically to keep cache size manageable

### 2. **10-Minute Advance Alerts**
- Background job checks every 60 seconds
- Identifies news events happening in 10-11 minutes
- Sends formatted notifications to all subscribed users
- Only alerts for HIGH and MEDIUM impact news

### 3. **News Risk Detection**
- Flags trades placed within ±10 minutes of HIGH/MEDIUM impact news
- Automatically applied when logging new trades
- Helps traders avoid risky timing

### 4. **Automatic Refresh**
- Scheduled daily at 00:05 UK time
- Fetches fresh news for the day
- Removes old news older than 1 day

## Commands

### User Commands
- `/news` - View all upcoming news events (next 24 hours)
- `/refreshnews` - Manually refresh news cache
- `/addnews [TIME] [TITLE] [CURRENCY] [IMPACT]` - Add news event manually

Example:
```
/addnews 2026-01-30 15:30 "US FOMC Statement" USD HIGH
```

### News Display Format
```
📰 Upcoming News (Next 24 Hours)

🔴 HIGH IMPACT
• 🇬🇧 UK GDP Growth Rate
  ⏰ 30 Jan 2026, 07:00

🟡 MEDIUM IMPACT
• 🇺🇸 US Unemployment Claims
  ⏰ 30 Jan 2026, 13:30

Last updated: 30 Jan 2026, 06:00
```

### News Alert Format
```
⚠️ NEWS ALERT - 10 Minutes Warning!

🔴 HIGH IMPACT
• 🇺🇸 US FOMC Statement
⏰ Event Time: 30 Jan 2026, 15:00

🚨 Avoid trading during high-impact news!
```

## Architecture

### Files Modified
1. **bot.py**
   - Added `import datetime` for job scheduling
   - User subscription system via `bot_data['subscribed_users']`
   - Job queue setup with `run_repeating` and `run_daily`
   - Welcome message updated to mention news alerts

2. **features/news_rule.py**
   - `load_news_cache()` - Returns dict with last_updated and news list
   - `save_news_cache()` - Saves news with timestamp
   - `fetch_daily_news()` - Orchestrates news fetching
   - `generate_sample_news_for_date()` - Demo sample data
   - `check_news_risk()` - Filters HIGH/MEDIUM impact only
   - `get_news_in_10_minutes()` - Targets 10-11 min window
   - `refresh_daily_news()` - Fetches today + tomorrow
   - `clean_old_news()` - Removes events older than 1 day

3. **features/admin_commands.py**
   - `show_upcoming_news()` - Lists upcoming events with impact emoji
   - `refresh_news_command()` - Manual refresh trigger
   - `add_news_event_command()` - Manual event addition (HIGH/MEDIUM only)
   - `send_news_alert()` - Background job for broadcasting alerts

4. **config.py**
   - `NEWS_RISK_WINDOW_MINUTES = 10` (changed from 30)
   - `NEWS_CACHE_PATH` for JSON storage

5. **requirements.txt**
   - Updated to `python-telegram-bot[job-queue]==20.7`
   - Added `requests==2.31.0`
   - Added `beautifulsoup4==4.12.3`

### Data Structure

#### News Cache Format (data/news_cache.json)
```json
{
  "last_updated": "2026-01-30 06:00:00",
  "news": [
    {
      "datetime": "2026-01-30 07:00:00",
      "title": "UK GDP Growth Rate",
      "currency": "GBP",
      "impact": "HIGH"
    },
    {
      "datetime": "2026-01-30 13:30:00",
      "title": "US Unemployment Claims",
      "currency": "USD",
      "impact": "MEDIUM"
    }
  ]
}
```

### Job Queue Configuration
```python
# News Alert Job - Runs every 60 seconds
application.job_queue.run_repeating(
    admin_commands.send_news_alert,
    interval=60,
    first=10,
    name='news_alerts'
)

# Daily Refresh Job - Runs at 00:05 UK time
application.job_queue.run_daily(
    refresh_news_callback,
    time=datetime.time(hour=0, minute=5),
    name='daily_news_refresh'
)
```

## Implementation Notes

### Current State
- ✅ Job queue system active
- ✅ Sample news generation working
- ✅ 10-minute alert system functional
- ✅ User subscription system active
- ✅ Daily refresh scheduled
- ✅ Manual commands working

### Future Enhancements (TODO)
1. **ForexFactory Integration**
   - Implement actual web scraping in `fetch_forexfactory_news()`
   - Replace sample data generation
   - Handle rate limiting and errors

2. **Additional Features**
   - User preference for impact levels (some may want LOW alerts)
   - Custom alert timing (5min, 15min options)
   - Historical news analysis
   - News correlation with trade results

3. **Optimization**
   - Cache expiry handling
   - Error recovery for failed fetches
   - Multiple news source support

## Testing Workflow

### Manual Testing
1. Start bot: `python bot.py`
2. Send `/start` to subscribe to alerts
3. Send `/news` to view upcoming events
4. Send `/refreshnews` to load fresh data
5. Wait for 10-minute alerts (or adjust sample news times for immediate testing)
6. Log a trade during risk window to see HIGH flag

### Sample News Timing
Current sample events are at:
- 07:00 (UK GDP - HIGH)
- 13:30 (US Claims - MEDIUM)
- 15:00 (US FOMC - HIGH)

To test alerts immediately, modify the times in `generate_sample_news_for_date()` to be 11-12 minutes in the future.

## Configuration

### Adjusting Alert Window
In `config.py`:
```python
NEWS_RISK_WINDOW_MINUTES = 10  # Change to 5, 15, etc.
```

### Adjusting Alert Frequency
In `bot.py`:
```python
application.job_queue.run_repeating(
    admin_commands.send_news_alert,
    interval=60,  # Change to 30 for 30-second checks
    first=10,
    name='news_alerts'
)
```

### Adjusting Daily Refresh Time
In `bot.py`:
```python
application.job_queue.run_daily(
    refresh_news_callback,
    time=datetime.time(hour=0, minute=5),  # Change hour/minute
    name='daily_news_refresh'
)
```

## Error Handling

### No News Cached
- Returns empty list
- No alerts sent
- Manual `/refreshnews` can fix

### Failed News Fetch
- Keeps existing cached news
- Logs error but continues running
- Next daily refresh will retry

### User Unsubscribe
- Currently automatic on `/start`
- Users cannot unsubscribe (feature not implemented)

## Emojis Used
- 📰 News/calendar
- ⚠️ Warning/alert
- 🔴 HIGH impact
- 🟡 MEDIUM impact
- 🔵 LOW impact
- 🇺🇸 🇬🇧 🇪🇺 Currency flags
- ⏰ Time/clock
- 🚨 Urgent warning
- 🔄 Refresh
- ➕ Add

## Conclusion
The news alert system is fully functional and ready for use. The main remaining task is to replace the sample news generation with actual ForexFactory scraping or API integration.
