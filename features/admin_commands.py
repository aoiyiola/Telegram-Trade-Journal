"""
Admin commands for managing news events
"""
from telegram import Update
from telegram.ext import ContextTypes
from features import news_rule
import utils


async def show_upcoming_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display upcoming high-impact news events."""
    upcoming = news_rule.get_upcoming_news(hours=24)
    
    if not upcoming:
        await update.message.reply_html(
            "📰 <b>Upcoming News (24h)</b>\n\n"
            "No high-impact news events scheduled.\n\n"
            "💡 Use /refreshnews to fetch today's news\n"
            "📝 Use /addnews to manually add an event"
        )
        return
    
    message = f"📰 <b>Upcoming News Events ({len(upcoming)})</b>\n\n"
    message += "⚠️ <i>Avoid trading ±10 min around these times</i>\n\n"
    
    for event in upcoming:
        time_str = utils.format_display_datetime(event['datetime'])
        impact_emoji = "🔴" if event.get('impact') == 'HIGH' else "🟡"
        message += (
            f"{impact_emoji} <b>{event['title']}</b>\n"
            f"📅 {time_str}\n"
        )
        if event.get('currency'):
            message += f"💱 {event['currency']}\n"
        message += f"⚡ Impact: {event.get('impact', 'HIGH')}\n\n"
    
    message += (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 You'll receive alerts 10 min before each event\n"
        "🛡️ Trades during risk windows will be flagged"
    )
    
    await update.message.reply_html(message)


async def refresh_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch and cache today's and tomorrow's news events."""
    await update.message.reply_html(
        "🔄 <b>Fetching news events...</b>\n\n"
        "Please wait..."
    )
    
    count = news_rule.refresh_daily_news()
    
    await update.message.reply_html(
        f"✅ <b>News Cache Updated</b>\n\n"
        f"📰 Loaded <b>{count}</b> news event(s)\n"
        f"📅 Coverage: Today + Tomorrow\n\n"
        "💡 Use /news to view upcoming events"
    )


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
    Called every minute by the job queue.
    """
    upcoming_news = news_rule.get_news_in_10_minutes()
    
    if not upcoming_news:
        return
    
    # Send alert to all users who have interacted with the bot
    # For now, we'll broadcast to the chat_id stored in bot_data
    chat_ids = context.bot_data.get('subscribed_users', set())
    
    for event in upcoming_news:
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
        
        alert_message += (
            f"\n⚡ Impact: <b>{event.get('impact', 'HIGH')}</b>\n\n"
            "🛑 <b>Avoid opening new trades</b>\n"
            "💡 Consider closing risky positions"
        )
        
        for chat_id in chat_ids:
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=alert_message,
                    parse_mode='HTML'
                )
            except Exception as e:
                print(f"Failed to send alert to {chat_id}: {e}")


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
