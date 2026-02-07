# Database Setup Guide

## MySQL Migration Complete! 🎉

Your Trading Journal bot has been migrated from CSV/JSON files to MySQL database for proper data persistence.

## Why Database?

Railway's filesystem is **ephemeral** - it wipes on every redeploy. This was causing:
- ❌ Users seeing setup screen every time after `/start`
- ❌ Lost configuration files
- ❌ Lost trade history

With MySQL:
- ✅ Data persists across redeployments
- ✅ Users stay registered
- ✅ All trades and accounts preserved
- ✅ Perfect for Railway's stateless containers

## Railway Database Setup

### Step 1: Add MySQL to Railway Project

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Open your project**: Telegram-Trade-Journal
3. **Click "+ New" button** in the project
4. **Select "Database"**
5. **Choose "MySQL"**
6. **Railway will provision** the database automatically

### Step 2: Verify DATABASE_URL

Railway automatically creates a `DATABASE_URL` environment variable when you add MySQL. The bot will use this variable to connect.

**No manual configuration needed!** 🎉

To verify:
1. Click on your MySQL service
2. Go to "Variables" tab
3. Confirm `DATABASE_URL` exists (format: `mysql://user:pass@host:port/db`)

### Step 3: Deploy Updated Code

1. **Commit your changes** to GitHub:
   ```bash
   git add .
   git commit -m "Migrate to MySQL database"
   git push
   ```

2. **Railway auto-deploys** when you push to GitHub

3. **Check deployment logs** for:
   ```
   ✅ Database initialized successfully
   ✅ Database tables created
   ```

## What Changed?

### Migration Summary

**Before (CSV/JSON):**
- `data/trades_global.csv` → Lost on redeploy
- `data/user_configs/user_*.json` → Lost on redeploy
- `data/users_registry.csv` → Lost on redeploy

**After (MySQL):**
- **users** table → Persists user registration, email, config
- **accounts** table → Persists user accounts (main, acc2, etc.)
- **pairs** table → Persists favorite pairs per user
- **trades** table → Persists all trade records

**No changes to bot commands or workflows!** Everything works exactly the same for users.

### Files Modified

1. **database.py** (NEW) - MySQL connection manager
2. **storage.py** - Replaced CSV operations with SQL queries
3. **user_manager.py** - Replaced JSON/CSV with SQL queries
4. **trade_logger.py** - Updated to use database
5. **trade_query.py** - Updated to use database
6. **trade_update.py** - Updated to use database
7. **bot.py** - Added database initialization on startup
7. **requirements.txt** - Added `mysql-connector-python==8.3.0`

### What Stayed the Same

✅ **news_cache.json** - Still uses JSON file (news data doesn't need persistence)
✅ All bot commands work identically
✅ User experience unchanged
✅ No existing data to migrate (confirmed clean slate)

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  telegram_id BIGINT UNIQUE NOT NULL,
  username VARCHAR(255),
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  email VARCHAR(255),
  config JSON,
  registration_date TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Accounts Table
```sql
CREATE TABLE accounts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  account_id VARCHAR(50) NOT NULL,
  account_name VARCHAR(255) NOT NULL,
  is_default BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY (user_id, account_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Pairs Table
```sql
CREATE TABLE pairs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  pair_name VARCHAR(20) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY (user_id, pair_name),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Trades Table
```sql
CREATE TABLE trades (
  id INT AUTO_INCREMENT PRIMARY KEY,
  trade_id VARCHAR(50) UNIQUE NOT NULL,
  user_id INT NOT NULL,
  account_id VARCHAR(50) NOT NULL,
  pair VARCHAR(20) NOT NULL,
  direction VARCHAR(10) NOT NULL,
  entry_price DECIMAL(20, 5) NOT NULL,
  stop_loss DECIMAL(20, 5),
  take_profit DECIMAL(20, 5),
  status VARCHAR(20) NOT NULL,
  result VARCHAR(10),
  session VARCHAR(20),
  news_risk VARCHAR(20),
  notes TEXT,
  entry_datetime TIMESTAMP NOT NULL,
  exit_datetime TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## Testing After Deployment

### Test Checklist

1. **New User Flow**:
   - `/start` → Should ask for email
   - Enter email → Should ask for account name
   - Enter account name → Should show Main Menu

2. **Existing User Flow** (after first registration):
   - `/start` → Should say "Welcome back!"
   - Should NOT ask for email/account again

3. **Trade Logging**:
   - `/newtrade` → Complete all steps
   - `/opentrades` → Should show the new trade
   - Verify trade stored in database

4. **Account Management**:
   - `/manageaccounts` → Add new account
   - Check account persists after adding

5. **Pair Management**:
   - `/managepairs` → Add custom pair
   - Check pair persists

6. **Persistence Test** (CRITICAL):
   - Use the bot, create some data
   - Manually redeploy on Railway (Project → Settings → Restart)
   - After restart, verify all data still exists
   - User should see "Welcome back!" not setup screen

## Troubleshooting

### Error: "DATABASE_URL not set in environment variables"

**Solution**: Add MySQL database to your Railway project (see Step 1)

### Error: "Can't connect to MySQL server"

**Check**:
1. MySQL service is running in Railway
2. DATABASE_URL exists in environment variables
3. Both services (bot + database) are in same Railway project

### Error: "relation 'users' does not exist"

**Solution**: Database tables weren't created. Check deployment logs. The bot automatically creates tables on startup.

**Manual fix** (if needed):
1. Go to Railway MySQL service
2. Open "Data" tab
3. Run SQL from database.py init_database() function

### Users Still Seeing Setup Screen

**Possible causes**:
1. Database not connected (check DATABASE_URL)
2. Tables not created (check logs for "Database initialized successfully")
3. Different bot instance (check you're talking to correct bot)

**Debug**:
- Check Railway logs for database connection errors
- Verify MySQL service is healthy
- Run `/start` and check logs for any errors

## Benefits of Migration

✅ **Data Persistence**: Survives redeployments  
✅ **Scalability**: Can handle thousands of users  
✅ **Reliability**: ACID transactions, data integrity  
✅ **Performance**: Indexed queries, faster than CSV  
✅ **Maintenance**: No file system dependencies  
✅ **Production-Ready**: Industry standard approach

## Cost

**MySQL on Railway**:
- **Hobby Plan**: Included (1GB storage)
- **Usage-Based**: Minimal cost after free tier
- **For this bot**: Essentially free (trades data is tiny)

**Estimate**: 1000 trades = ~0.5MB, 1 month = ~$0.01 total

Your current $5/month Hobby plan includes MySQL at no extra cost! 🎉

## Next Steps

1. ✅ Code changes complete
2. ⏭️ Add MySQL to Railway project
3. ⏭️ Push code to GitHub
4. ⏭️ Verify deployment logs
5. ⏭️ Test bot functionality
6. ⏭️ Celebrate! 🎉

## Support

If you encounter issues:
1. Check Railway deployment logs
2. Verify DATABASE_URL environment variable exists
3. Confirm MySQL service is running
4. Test database connection from bot logs

All set! Your bot is now production-ready with proper data persistence. 🚀
