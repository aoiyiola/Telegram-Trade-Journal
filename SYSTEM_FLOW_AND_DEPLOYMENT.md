# Trading Journal System - Complete Flow & Deployment Guide

## 🚀 System Start Flow

### 1. **Entry Point: `start.py`**

When Railway starts your application, it runs `start.py`:

```
Railway Deployment
    ↓
start.py (main entry)
    ↓
    ├── Thread 1: Web Server (Flask) - Port 8080
    │   ├── Serves React dashboard at /
    │   ├── API endpoints at /api/dashboard/<token>
    │   └── Handles dashboard token generation
    │
    └── Main Thread: Telegram Bot
        ├── Connects to Telegram API
        ├── Initializes MySQL database
        ├── Loads news cache (60 seconds after start)
        ├── Sets up command handlers
        ├── Starts news alert system (every 60s)
        └── Listens for user messages
```

### 2. **Telegram Bot Flow**

#### **New User Registration:**
```
User sends /start
    ↓
Check: user_exists_in_registry(user_id)
    ↓
    NO → New User Flow:
        1. Show welcome message
        2. Only "Start" button visible
        3. Ask for email → handle_setup_email()
        4. Ask for account name → handle_setup_account_name()
        5. Call register_user() → Creates DB entries:
           - users table (with email)
           - accounts table (default "Main Account")
           - pairs table (EURUSD, GBPUSD, XAUUSD, USDJPY)
        6. Show full command menu → set_user_commands()
        7. Registration complete ✅
    ↓
    YES → Existing User Flow:
        1. Show welcome message
        2. Full command menu visible immediately
        3. Ready to use bot
```

#### **Trade Logging Flow:**
```
User sends /newtrade
    ↓
1. SELECT_ACCOUNT: Choose trading account
    ↓
2. SELECT_PAIR: Choose currency pair
    ↓
3. DIRECTION: Select BUY or SELL
    ↓
4. ENTRY: Enter entry price
    ↓
5. STOP_LOSS: Enter stop loss (or skip)
    ↓
6. TAKE_PROFIT: Enter take profit (or skip)
    ↓
7. NOTES: Add trade notes (optional)
    ↓
Auto-detect:
    - Trading session (Asia/London/NY) → session_tag.py
    - News risk (within 60 min of high-impact news) → news_rule.py
    ↓
Save to MySQL trades table
    ↓
Send confirmation message with trade details
```

#### **Dashboard Generation Flow:**
```
User sends /dashboard
    ↓
generate_dashboard_link() in admin_commands.py
    ↓
1. Get user's telegram_id
2. Generate secure token (secrets.token_urlsafe)
3. Store token in active_tokens dict:
   {
     token: {
       telegram_id: 12345,
       expires: datetime + 24 hours
     }
   }
4. Build dashboard URL: https://your-app.railway.app/dashboard?token=XYZ
5. Send link to user via Telegram
    ↓
User clicks link
    ↓
React app loads with token parameter
    ↓
App makes API call: GET /api/dashboard/{token}
    ↓
Backend verifies token:
    - Check if token exists
    - Check if not expired
    - Get telegram_id from token
    ↓
Query MySQL:
    - Get user info
    - Get all trades
    - Calculate statistics (win rate, etc.)
    - Group by pair, session
    - Get accounts
    ↓
Return JSON response to React
    ↓
React renders dashboard with charts and tables
```

### 3. **News System Flow**

```
Bot starts
    ↓
T+0s: init_sample_news() creates initial cache
    ↓
T+10s: News alert system starts (runs every 60s)
    ↓
T+60s: First news refresh from FCS API
    - Fetches today's HIGH/MEDIUM impact events
    - Stores in news_cache.json
    - Updates database
    ↓
Every 60 seconds:
    - get_news_in_10_minutes() checks for upcoming events
    - If event in next 10-11 minutes:
        → Send alert to all subscribed users
        → Mark event as alerted (prevent duplicates)
    ↓
Every 4 hours:
    - refresh_daily_news() fetches fresh data
    - Clears old alerted events
    ↓
When user sends /news:
    - get_todays_news() filters events for today
    - Shows formatted calendar with times
    - Marks past/upcoming events
```

### 4. **Database Flow**

```
Application Startup
    ↓
database.init_database()
    ↓
Creates tables if not exist:
    - users (telegram_id, email, config)
    - accounts (user_id, account_name, is_default)
    - pairs (user_id, pair_name)
    - trades (all trade data)
    ↓
Creates indexes for performance:
    - idx_trades_user_id
    - idx_trades_status
    - idx_trades_entry_datetime
```

---

## 🛠️ Railway Deployment Steps

### **Prerequisites:**
1. ✅ GitHub repository with all code
2. ✅ Railway account (free tier works)
3. ✅ FCS API key (for news)
4. ✅ Telegram bot token

### **Step 1: Add Railway Configuration**

Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "cd web && npm install && npm run build && cd .."
  },
  "deploy": {
    "startCommand": "python start.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Create `Procfile`:
```
web: python start.py
```

### **Step 2: Build React App Locally (Optional Pre-test)**

```bash
cd web
npm install
npm run build
cd ..
```

This creates `web/dist/` folder with production-ready React app.

### **Step 3: Deploy to Railway**

1. **Create New Project:**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `aoiyiola/Telegram-Trade-Journal`

2. **Add MySQL Database:**
   - Click "+ New" in your project
   - Select "Database" → "MySQL"
   - Railway auto-creates `DATABASE_URL` variable

3. **Set Environment Variables:**
   
   Go to Variables tab, add:
   ```
   TELEGRAM_BOT_TOKEN=8486815486:AAGTVKEQut5Bx5IkZ0e3gKBasg4MJTuOFH4
   FCS_API_KEY=your_fcs_api_key_here
   DATABASE_URL=<auto-generated by Railway>
   PORT=8080
   RAILWAY_PUBLIC_DOMAIN=<your-app-name>.railway.app
   ```

4. **Configure Build Settings:**
   - Build Command: `cd web && npm install && npm run build && cd ..`
   - Start Command: `python start.py`
   - Root Directory: `/`

5. **Generate Public Domain:**
   - Go to Settings → Networking
   - Click "Generate Domain"
   - Copy domain: `your-app.up.railway.app`
   - Add this to `RAILWAY_PUBLIC_DOMAIN` variable

### **Step 4: Verify Deployment**

Check logs for:
```
✅ Database initialized successfully
✅ News cache initialized successfully
✅ Bot commands menu set (default)
🌐 Starting web server on port 8080
🤖 Starting Telegram bot...
✅ Web server thread started
```

### **Step 5: Test the System**

1. **Test Telegram Bot:**
   ```
   /start → Should show setup flow
   Complete registration
   /newtrade → Log a test trade
   /dashboard → Get dashboard link
   ```

2. **Test Dashboard:**
   - Click dashboard link from Telegram
   - Should load React app with your data
   - Check mobile responsiveness
   - Verify charts and tables display correctly

### **Step 6: Update Bot Commands Menu**

The bot automatically sets commands, but verify:
- New users see only `/start`
- Registered users see full menu including `/dashboard`

---

## 📱 How Users Access Dashboard

### **From Telegram:**
```
1. User sends /dashboard command
2. Bot generates secure 24-hour token
3. Bot sends clickable link
4. User clicks → Opens in browser
5. Dashboard loads with their data
6. Works on mobile & desktop
```

### **Security:**
- Each token is unique and user-specific
- Tokens expire after 24 hours
- Token required for API access
- No login needed (token-based auth)

---

## 🔄 Auto-Deploy Workflow

```
1. Push code to GitHub
   ↓
2. Railway detects changes
   ↓
3. Railway builds:
   - Installs Python dependencies
   - cd web && npm install
   - npm run build (React)
   - Creates production bundle
   ↓
4. Railway deploys:
   - Starts start.py
   - Web server + Bot both running
   ↓
5. Health check passes
   ↓
6. Live! ✅
```

---

## 📊 System Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                    Railway App                       │
│                                                      │
│  ┌──────────────┐          ┌──────────────────────┐│
│  │   start.py   │          │                      ││
│  │   (Main)     │          │                      ││
│  └──────┬───────┘          │                      ││
│         │                  │                      ││
│         │                  │                      ││
│    ┌────┴────┐            │                      ││
│    │         │            │                      ││
│    ▼         ▼            │                      ││
│ ┌────┐   ┌──────┐        │    Railway MySQL    ││
│ │Bot │   │Flask │        │                      ││
│ │    │   │Web   │◄───────┤    ┌──────────────┐ ││
│ │    │   │Server│        │    │  users        │ ││
│ │    │   │      │        │    │  accounts     │ ││
│ │    │   │Serves│        │    │  pairs        │ ││
│ │    │   │React │        │    │  trades       │ ││
│ └─┬──┘   └──┬───┘        │    └──────────────┘ ││
│   │         │            │                      ││
│   │         │            └──────────────────────┘│
│   │         │                                     │
└───┼─────────┼─────────────────────────────────────┘
    │         │
    │         │
    ▼         ▼
┌─────────┐ ┌──────────┐
│Telegram │ │ Browser  │
│ Users   │ │Dashboard │
└─────────┘ └──────────┘
```

---

## 🎯 Quick Deploy Checklist

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] MySQL database added
- [ ] Environment variables set
- [ ] Domain generated
- [ ] Build commands configured
- [ ] Deployment successful
- [ ] Logs show no errors
- [ ] Test /start command
- [ ] Test /newtrade command
- [ ] Test /dashboard command
- [ ] Dashboard opens in browser
- [ ] Data displays correctly
- [ ] Mobile responsive works

---

## 🔧 Troubleshooting

### **Bot not responding:**
- Check `TELEGRAM_BOT_TOKEN` is correct
- Verify logs for connection errors
- Ensure DATABASE_URL is set

### **Dashboard shows "Invalid token":**
- Token expired (24 hours)
- Generate new link with `/dashboard`

### **Charts not loading:**
- Check browser console for errors
- Verify API endpoint returns data
- Test: `curl https://your-app.railway.app/api/dashboard/test`

### **Build fails:**
- Check Node.js version (should use latest)
- Verify package.json dependencies
- Check build logs for npm errors

---

## 📞 Support Commands

- `/start` - Register or welcome message
- `/newtrade` - Log a new trade
- `/opentrades` - View open positions
- `/recenttrades` - Recent trade history
- `/updatetrade` - Update trade result (W/L/BE)
- `/managepairs` - Add/remove trading pairs
- `/manageaccounts` - Add/rename accounts
- `/news` - Today's economic calendar
- `/dashboard` - Generate dashboard link
- `/help` - Full command list

---

**System is production-ready!** 🚀
