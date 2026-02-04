"""
News rule module - Detect high-impact news and flag trades
Fetches daily news events and sends notifications 10 minutes before
"""
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import config
import utils


def load_news_cache() -> Dict:
    """
    Load cached news data from JSON file.
    
    Returns:
        Dictionary with last_updated and news list
    """
    if not os.path.exists(config.NEWS_CACHE_PATH):
        return {'last_updated': None, 'news': []}
    
    try:
        with open(config.NEWS_CACHE_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {'last_updated': None, 'news': []}


def save_news_cache(news_events: List[Dict], last_updated: str = None) -> None:
    """
    Save news data to cache file.
    
    Args:
        news_events: List of news event dictionaries
        last_updated: Optional timestamp, defaults to current time
    """
    os.makedirs(os.path.dirname(config.NEWS_CACHE_PATH), exist_ok=True)
    
    if last_updated is None:
        last_updated = utils.get_current_datetime_string()
    
    cache_data = {
        'last_updated': last_updated,
        'news': news_events
    }
    
    with open(config.NEWS_CACHE_PATH, 'w') as f:
        json.dump(cache_data, f, indent=2)


def fetch_fcs_api_news(date_str: str) -> List[Dict]:
    """
    Fetch news from FCS API economic calendar.
    
    Args:
        date_str: Date string in format 'YYYY-MM-DD'
    
    Returns:
        List of news event dictionaries
    """
    if not config.FCS_API_KEY:
        print("⚠️ FCS_API_KEY not set. Using sample data.")
        return []
    
    url = "https://fcsapi.com/api-v3/economy/calendar"
    params = {
        'access_key': config.FCS_API_KEY,
        'date_from': date_str,
        'date_to': date_str,
        'impact': 'high,medium'  # Only HIGH and MEDIUM impact
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') != True:
            print(f"❌ FCS API Error: {data.get('msg', 'Unknown error')}")
            return []
        
        news_events = []
        for event in data.get('response', []):
            # Parse FCS API response
            event_date = event.get('date', '')
            event_time = event.get('time', '')
            
            # Combine date and time
            datetime_str = f"{event_date} {event_time}"
            
            # Convert to our format
            try:
                event_dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
                formatted_datetime = utils.format_datetime(event_dt)
            except ValueError:
                print(f"⚠️ Invalid datetime format: {datetime_str}")
                continue
            
            news_events.append({
                'datetime': formatted_datetime,
                'title': event.get('name', 'Unknown Event'),
                'currency': event.get('country', 'USD'),
                'impact': event.get('impact', 'MEDIUM').upper()
            })
        
        print(f"✅ Fetched {len(news_events)} events from FCS API for {date_str}")
        return news_events
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching from FCS API: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []


def fetch_daily_news() -> List[Dict]:
    """
    Fetch HIGH and MEDIUM impact news for today only from FCS API.
    No fallback to sample data.
    
    Returns:
        List of news event dictionaries (empty if API fails)
    """
    if not config.FCS_API_KEY:
        print("⚠️ FCS_API_KEY not set")
        return []
    
    news_events = []
    current_date = utils.get_current_uk_time().date()
    date_str = current_date.strftime('%Y-%m-%d')
    
    # Fetch only today's news from FCS API
    fcs_news = fetch_fcs_api_news(date_str)
    if fcs_news:
        news_events.extend(fcs_news)
        print(f"✅ Fetched {len(fcs_news)} events for today from FCS API")
    else:
        print(f"❌ Failed to fetch news for {date_str} from API")
    
    return news_events


def generate_sample_news_for_date(base_date: datetime) -> List[Dict]:
    """
    Generate sample news events for testing.
    
    Args:
        base_date: Base datetime to generate news around
    
    Returns:
        List of sample news event dictionaries
    """
    base_time = base_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    sample_events = [
        {
            'datetime': utils.format_datetime(base_time + timedelta(hours=7, minutes=0)),
            'title': 'UK GDP Growth Rate',
            'currency': 'GBP',
            'impact': 'HIGH'
        },
        {
            'datetime': utils.format_datetime(base_time + timedelta(hours=13, minutes=30)),
            'title': 'US Unemployment Claims',
            'currency': 'USD',
            'impact': 'MEDIUM'
        },
        {
            'datetime': utils.format_datetime(base_time + timedelta(hours=15, minutes=0)),
            'title': 'US FOMC Statement',
            'currency': 'USD',
            'impact': 'HIGH'
        }
    ]
    
    return sample_events


def init_sample_news() -> None:
    """Initialize news cache by fetching real data from API."""
    try:
        print("🔄 Initializing news cache with real API data...")
        
        if not config.FCS_API_KEY:
            print("⚠️ FCS_API_KEY not set - News feature disabled")
            save_news_cache([])  # Empty cache
            return
        
        # Fetch real news from API
        all_news = fetch_daily_news()
        
        if not all_news:
            print("⚠️ No news fetched from API - News feature unavailable")
            save_news_cache([])  # Empty cache
            return
            
        save_news_cache(all_news)
        print(f"✅ Initialized {len(all_news)} real news events from API")
    except Exception as e:
        print(f"❌ Error in init_sample_news: {e}")
        save_news_cache([])  # Empty cache on error


def check_news_risk(trade_time: datetime) -> str:
    """
    Check if a trade time is within the news risk window.
    Only checks for HIGH and MEDIUM impact news.
    
    Args:
        trade_time: The datetime when the trade was/will be placed
    
    Returns:
        'HIGH' if within risk window of HIGH/MEDIUM impact news, 'LOW' otherwise
    """
    cache_data = load_news_cache()
    news_events = cache_data.get('news', [])
    
    risk_window_minutes = config.NEWS_RISK_WINDOW_MINUTES
    
    for event in news_events:
        try:
            # Skip LOW impact news
            if event.get('impact') not in ['HIGH', 'MEDIUM']:
                continue
            
            event_time = utils.parse_datetime(event['datetime'])
            time_diff = abs((trade_time - event_time).total_seconds() / 60)
            
            if time_diff <= risk_window_minutes:
                return 'HIGH'
        except (KeyError, ValueError):
            continue
    
    return 'LOW'


def get_todays_news() -> List[Dict]:
    """
    Get all news events for today only.
    
    Returns:
        List of today's news events sorted by datetime, or None if error/no API key
    """
    cache_data = load_news_cache()
    news_events = cache_data.get('news', [])
    
    if not news_events:
        print("⚠️ No news events in cache")
        return None  # Return None to indicate error state
    
    current_time = utils.get_current_uk_time()
    today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    print(f"📅 Getting today's news: {today_start.strftime('%Y-%m-%d')}")
    print(f"📰 Total events in cache: {len(news_events)}")
    
    todays_events = []
    for event in news_events:
        try:
            event_time = utils.parse_datetime(event['datetime'])
            if today_start <= event_time < today_end:
                todays_events.append(event)
                print(f"✅ Today's event: {event['title']} at {event['datetime']}")
        except (KeyError, ValueError) as e:
            print(f"❌ Error parsing event: {e}")
            continue
    
    print(f"🔍 Found {len(todays_events)} events for today")
    
    # Sort by datetime
    todays_events.sort(key=lambda x: x['datetime'])
    return todays_events


def get_news_in_10_minutes() -> List[Dict]:
    """
    Get news events that will occur in 10-11 minutes.
    This is used by the alert system to notify users.
    
    Returns:
        List of news events happening in 10-11 minutes
    """
    cache_data = load_news_cache()
    news_events = cache_data.get('news', [])
    
    if not news_events:
        return []
    
    current_time = utils.get_current_uk_time()
    min_time = current_time + timedelta(minutes=10)
    max_time = current_time + timedelta(minutes=11)
    
    alert_events = []
    for event in news_events:
        try:
            # Only alert for HIGH and MEDIUM impact
            if event.get('impact') not in ['HIGH', 'MEDIUM']:
                continue
            
            event_time = utils.parse_datetime(event['datetime'])
            if min_time <= event_time < max_time:
                alert_events.append(event)
        except (KeyError, ValueError):
            continue
    
    return alert_events


def add_news_event(datetime_str: str, title: str, currency: str, impact: str) -> bool:
    """
    Manually add a news event to the cache.
    
    Args:
        datetime_str: Event datetime string
        title: News event title
        currency: Currency affected (e.g., 'USD', 'GBP')
        impact: Impact level ('HIGH' or 'MEDIUM')
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Validate datetime
        utils.parse_datetime(datetime_str)
        
        # Validate impact
        if impact not in ['HIGH', 'MEDIUM']:
            return False
        
        # Load current cache
        cache_data = load_news_cache()
        news_events = cache_data.get('news', [])
        
        # Create new event
        new_event = {
            'datetime': datetime_str,
            'title': title,
            'currency': currency,
            'impact': impact
        }
        
        # Add to events
        news_events.append(new_event)
        
        # Sort by datetime
        news_events.sort(key=lambda x: x['datetime'])
        
        # Save back to cache
        save_news_cache(news_events, cache_data.get('last_updated'))
        
        return True
    except Exception as e:
        print(f"Error adding news event: {e}")
        return False


def clean_old_news(days_to_keep: int = 1) -> None:
    """
    Remove news events older than specified days.
    
    Args:
        days_to_keep: Number of days of news to keep
    """
    cache_data = load_news_cache()
    news_events = cache_data.get('news', [])
    
    if not news_events:
        return
    
    cutoff_date = utils.get_current_uk_time() - timedelta(days=days_to_keep)
    
    filtered_events = []
    for event in news_events:
        try:
            event_time = utils.parse_datetime(event['datetime'])
            if event_time >= cutoff_date:
                filtered_events.append(event)
        except (KeyError, ValueError):
            continue
    
    save_news_cache(filtered_events, cache_data.get('last_updated'))


def refresh_daily_news() -> List[Dict]:
    """
    Refresh news cache with latest HIGH and MEDIUM impact news.
    Fetches news for today and tomorrow.
    
    Returns:
        List of fetched news events
    """
    print("🔄 Refreshing daily news cache...")
    
    # Clean old news first
    clean_old_news(days_to_keep=1)
    
    # Fetch new news from FCS API or sample data
    all_news = fetch_daily_news()
    save_news_cache(all_news)
    
    print(f"✅ News cache refreshed with {len(all_news)} events")
    return all_news
