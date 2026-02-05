"""
Admin commands for managing news events
"""
from telegram import Update
from telegram.ext import ContextTypes
from features import news_rule
import utils


async def show_upcoming_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display today's high-impact news events with beautiful formatting."""
    try:
        todays_news, api_available = news_rule.get_todays_news()
        
        # Check if API is unavailable
        if not api_available:
            await update.message.reply_html(
                "⚠️ <b>News Feature Status</b>\n\n"
                "📰 News addon is on hold, please check back later.\n\n"
                "💡 The news service will be available soon."
            )
            return
        
        # Check if no events today (but API is working)
        if not todays_news:
            current_date = utils.get_current_uk_time().strftime('%A, %B %d, %Y')
            await update.message.reply_html(
                f"📰 <b>Today's Economic News</b>\n"
                f"📅 {current_date}\n\n"
                "✅ <i>No high-impact news events scheduled today</i>\n\n"
                "🟢 Safe to trade without news risk concerns!\n\n"
                "💡 News updates automatically every 4 hours"
            )
            return
        
        # Build beautiful message with today's news
        current_date = utils.get_current_uk_time().strftime('%A, %B %d, %Y')
        current_time = utils.get_current_uk_time()
        
        message = (
            f"📰 <b>Today's Economic Calendar</b>\n"
            f"📅 {current_date}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        
        for idx, event in enumerate(todays_news, 1):
            event_time = utils.parse_datetime(event['datetime'])
            time_str = event_time.strftime('%H:%M')
            
            # Determine if event has passed
            if event_time < current_time:
                status_emoji = "✅"
                status = "Completed"
            else:
                status_emoji = "🔴"
                status = "Upcoming"
            
            # Impact emoji
            impact = event.get('impact', 'HIGH')
            if impact == 'HIGH':
                impact_emoji = "🔴"
                impact_text = "<b>HIGH</b>"
            else:
                impact_emoji = "🟡"
                impact_text = "MEDIUM"
            
            currency = event.get('currency', 'USD')
            title = event['title']
            
            message += (
                f"{status_emoji} <b>{time_str}</b> - {status}\n"
                f"{impact_emoji} Impact: {impact_text}\n"
                f"💱 Currency: <code>{currency}</code>\n"
                f"📋 {title}\n\n"
            )
        
        message += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔔 <i>You'll receive alerts 10 minutes before each event</i>\n"
            "🛡️ <i>Trades during news windows will be flagged automatically</i>\n\n"
            "💡 News updates refresh every 4 hours"
        )
        
        await update.message.reply_html(message)
        
    except Exception as e:
        await update.message.reply_html(
            f"❌ <b>Error Loading News</b>\n\n"
            f"📰 News addon is on hold, please check back later.\n\n"
            "💡 The service will be restored shortly."
        )
        print(f"❌ Error in show_upcoming_news: {e}")
        return




async def add_news_event_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Manually add a news event.
    Format: /addnews YYYY-MM-DD HH:MM IMPACT Title
    """
    if not context.args or len(context.args) < 4:
        await update.message.reply_html(
            "❌ <b>Invalid format</b>\n\n"
            "Usage:\n"
            "<code>/addnews YYYY-MM-DD HH:MM IMPACT Title</code>\n\n"
            "IMPACT: HIGH or MEDIUM\n\n"
            "Example:\n"
            "<code>/addnews 2026-01-30 14:30 HIGH US Fed Rate Decision</code>"
        )
        return
    
    try:
        # Parse date and time
        date_str = context.args[0]
        time_str = context.args[1]
        datetime_str = f"{date_str} {time_str}:00"
        
        # Validate datetime
        utils.parse_datetime(datetime_str)
        
        # Get impact
        impact = context.args[2].upper()
        if impact not in ['HIGH', 'MEDIUM']:
            raise ValueError("Impact must be HIGH or MEDIUM")
        
        # Get title
        title = ' '.join(context.args[3:])
        
        # Add to cache
        news_rule.add_news_event(datetime_str, title, impact=impact)
        
        impact_emoji = "🔴" if impact == 'HIGH' else "🟡"
        
        await update.message.reply_html(
            f"✅ <b>News Event Added</b>\n\n"
            f"{impact_emoji} <b>{title}</b>\n"
            f"📅 {utils.format_display_datetime(datetime_str)}\n"
            f"⚡ Impact: {impact}\n\n"
            "Trades within ±10 min will be flagged as HIGH risk.\n"
            "You'll receive an alert 10 min before this event."
        )
    except (ValueError, IndexError) as e:
        await update.message.reply_html(
            f"❌ <b>Error adding news event</b>\n\n"
            f"{str(e)}\n\n"
            "Please check the format:\n"
            "<code>/addnews YYYY-MM-DD HH:MM HIGH/MEDIUM Title</code>"
        )


async def send_news_alert(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Background job to check for upcoming news and send alerts.
    Runs every minute (this is intentional) to catch news 10 minutes before.
    Only sends alerts when news is actually upcoming.
    Ensures each news event alert is sent only ONCE.
    """
    upcoming_news = news_rule.get_news_in_10_minutes()
    
    if not upcoming_news:
        # No news in the next 10-11 minutes - this is normal, don't log
        return
    
    # Initialize alerted events tracker if not exists
    if 'alerted_news_events' not in context.bot_data:
        context.bot_data['alerted_news_events'] = set()
    
    # Send alert to all users who have interacted with the bot
    chat_ids = context.bot_data.get('subscribed_users', set())
    
    for event in upcoming_news:
        # Create unique identifier for this event (datetime + title)
        event_id = f"{event['datetime']}_{event['title']}"
        
        # Check if alert already sent for this event
        if event_id in context.bot_data['alerted_news_events']:
            # Already alerted, skip
            continue
        
        # Mark as alerted
        context.bot_data['alerted_news_events'].add(event_id)
        
        impact_emoji = "🔴" if event.get('impact') == 'HIGH' else "🟡"
        time_str = utils.format_display_datetime(event['datetime'])
        
        alert_message = (
            f"⚠️ <b>NEWS ALERT</b> ⚠️\n\n"
            f"{impact_emoji} <b>{event['title']}</b>\n"
            f"📅 Time: {time_str}\n"
            f"⏰ In: <b>~10 minutes</b>\n"
        )
        
        if event.get('currency'):
            alert_message += f"💱 Currency: {event['currency']}\n"
        
        alert_message += f"\n⚡ Impact: <b>{event.get('impact', 'HIGH')}</b>"
        
        for chat_id in chat_ids:
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=alert_message,
                    parse_mode='HTML'
                )
            except Exception as e:
                print(f"Failed to send alert to {chat_id}: {e}")
        
        print(f"✅ Alert sent for: {event['title']} at {event['datetime']}")


async def refresh_news_cache_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Background job to refresh news cache every 4 hours.
    Ensures we always have up-to-date news data.
    Also cleans up old alerted events from memory.
    """
    try:
        print("🔄 Running scheduled news refresh...")
        count = news_rule.refresh_daily_news()
        if count > 0:
            print(f"✅ News cache refreshed: {count} events loaded")
        else:
            print("ℹ️ News cache refreshed: No events today")
        
        # Clean up old alerted events (older than 2 hours)
        if 'alerted_news_events' in context.bot_data:
            old_count = len(context.bot_data['alerted_news_events'])
            # Clear all old alerts on refresh (they're already past)
            context.bot_data['alerted_news_events'].clear()
            if old_count > 0:
                print(f"🧹 Cleared {old_count} old alert records")
    except Exception as e:
        print(f"❌ Failed to refresh news cache: {e}")


async def send_daily_news_summary(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send daily news summary to all subscribed users after news refresh.
    Called daily after news fetch.
    """
    # Refresh news first
    all_news = news_rule.refresh_daily_news()
    
    if not all_news:
        return
    
    # Group by impact
    high_impact = [n for n in all_news if n.get('impact') == 'HIGH']
    medium_impact = [n for n in all_news if n.get('impact') == 'MEDIUM']
    
    # Create summary message
    message = (
        "📰 <b>Today's Economic Calendar</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 <b>Total Events: {len(all_news)}</b>\n"
        f"🔴 HIGH Impact: {len(high_impact)}\n"
        f"🟡 MEDIUM Impact: {len(medium_impact)}\n\n"
    )
    
    # Add HIGH impact events
    if high_impact:
        message += "🔴 <b>HIGH IMPACT EVENTS</b>\n\n"
        for event in high_impact:
            time_str = utils.format_display_datetime(event['datetime'])
            message += f"• <b>{event['title']}</b>\n"
            message += f"  ⏰ {time_str}\n"
            if event.get('currency'):
                message += f"  💱 {event['currency']}\n"
            message += "\n"
    
    # Add MEDIUM impact events
    if medium_impact:
        message += "🟡 <b>MEDIUM IMPACT EVENTS</b>\n\n"
        for event in medium_impact:
            time_str = utils.format_display_datetime(event['datetime'])
            message += f"• <b>{event['title']}</b>\n"
            message += f"  ⏰ {time_str}\n"
            if event.get('currency'):
                message += f"  💱 {event['currency']}\n"
            message += "\n"
    
    message += (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ You'll receive alerts 10 min before each event\n"
        "🛡️ Trades during ±10 min windows will be flagged"
    )
    
    # Send to all subscribed users
    chat_ids = context.bot_data.get('subscribed_users', set())
    for chat_id in chat_ids:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Failed to send daily summary to {chat_id}: {e}")
