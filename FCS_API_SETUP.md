# FCS API Setup Guide

## What is FCS API?
FCS API (Financial Content Services) provides real-time economic calendar data with high, medium, and low impact events. Perfect for forex and crypto traders who need to avoid volatile news periods.

## Why FCS API?
- ✅ **Free Tier**: 500 API calls/month
- ✅ **Perfect for Daily Use**: 1-2 calls/day = only 30-60 calls/month
- ✅ **Clean Data**: Structured JSON with impact levels
- ✅ **Reliable**: Professional service with good uptime
- ✅ **No Credit Card**: Free tier doesn't require payment info

## Setup Instructions

### Step 1: Sign Up (2 minutes)
1. Go to https://fcsapi.com
2. Click **"Sign Up"** or **"Get Started"**
3. Create account with email
4. Verify your email

### Step 2: Get API Key (1 minute)
1. Log in to your FCS API dashboard
2. Go to **"API Keys"** or **"Dashboard"**
3. Copy your **Access Key**
4. It looks like: `abc123xyz456def789ghi012jkl345mno678`

### Step 3: Add to Bot (.env file)
1. Open the `.env` file in your project root
2. Add your API key:
   ```
   FCS_API_KEY=your_actual_key_here
   ```
3. Save the file

### Step 4: Test
Run the bot and use `/refreshnews` command. You should see:
```
✅ Fetched X events from FCS API for 2026-02-04
```

## Free Tier Limits
- **500 calls/month**
- **17 calls/day** (average)
- **Bot uses 1-2 calls/day** (fetch today + tomorrow)
- **Usage**: ~4-12% of monthly quota

## What If I Don't Add the API Key?
No problem! The bot will automatically use **sample data** for testing:
- 3 demo news events per day
- HIGH and MEDIUM impact examples
- All features work the same

## Upgrade Later
If you need more calls:
- **Starter Plan**: $10/month (5,000 calls)
- **Basic Plan**: $25/month (15,000 calls)

For this bot's daily usage, **free tier is perfect forever**.

## Troubleshooting

### "❌ FCS API Error: Invalid API Key"
- Check you copied the full key
- Verify it's in `.env` file as `FCS_API_KEY=...`
- Restart the bot after adding the key

### "⚠️ FCS_API_KEY not set. Using sample data."
- This is fine for testing
- Add the API key when you're ready for real data

### "❌ Error fetching from FCS API: Connection timeout"
- Check your internet connection
- FCS API might be temporarily down
- Bot will use cached data from yesterday

## Need Help?
- FCS API Docs: https://fcsapi.com/document/economy-api
- Support: support@fcsapi.com
- Bot issues: Create GitHub issue

## Example API Response
```json
{
  "status": true,
  "response": [
    {
      "date": "2026-02-04",
      "time": "13:30:00",
      "name": "US Non-Farm Payrolls",
      "country": "USD",
      "impact": "HIGH"
    }
  ]
}
```
