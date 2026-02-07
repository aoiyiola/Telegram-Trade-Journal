# Railway MySQL Setup Guide 🚀

## Complete Step-by-Step Instructions

Your bot is now configured to use **MySQL** database for data persistence.

---

## 📋 Prerequisites

- Railway.app account (already have this)
- GitHub repository connected to Railway (already done)
- Your bot project deployed on Railway

---

## 🔧 Step 1: Add MySQL Database to Railway

### Via Railway Dashboard

1. **Login to Railway**: https://railway.app/dashboard

2. **Open your project**: Click on "Telegram-Trade-Journal"

3. **Add MySQL database**:
   - Click the **"+ New"** button in your project
   - Select **"Database"**
   - Choose **"MySQL"**
   - Railway will automatically provision the database (takes ~30 seconds)

4. **Verify database created**:
   - You should see a new service card named "MySQL" in your project
   - It will show status as "Active" when ready

---

## 🔗 Step 2: Verify Environment Variable

Railway automatically creates the `DATABASE_URL` environment variable when you add MySQL.

### To confirm:

1. **Click on MySQL service** (the database card)
2. Click **"Variables"** tab
3. Look for **`DATABASE_URL`**
4. Format should be: `mysql://user:password@host:port/database`

**✅ If you see it, you're good!** Railway handles the connection automatically.

---

## 📤 Step 3: Deploy Your Code

Now push the updated code to GitHub:

```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Switch to MySQL database for persistence"

# Push to GitHub
git push origin main
```

**Railway will auto-deploy** when it detects the push (~2-3 minutes).

---

## 📊 Step 4: Monitor Deployment

### Check Deployment Logs

1. **Go to Railway Dashboard**
2. **Click on your bot service** (not the MySQL one)
3. **Click "Deployments"** tab
4. **View latest deployment**

### Look for these success messages in logs:

```
✅ Database initialized successfully
✅ Database tables created
✅ News cache initialized successfully
🚀 Trading Journal Bot is starting...
```

**If you see these, deployment succeeded!** 🎉

### If you see errors:

- **"DATABASE_URL not set"**: Wait 30 seconds, Railway might still be linking services
- **"Connection refused"**: MySQL service might still be starting, give it 1-2 minutes
- **Other errors**: Check the troubleshooting section below

---

## 🧪 Step 5: Test Your Bot

### Test 1: New User Registration

1. **Open Telegram** and find your bot
2. Send: `/start`
3. **Expected**: "Welcome! Please provide your email"
4. Send your email: `youremail@example.com`
5. **Expected**: "Please enter your first account name"
6. Send account name: `My Trading Account`
7. **Expected**: Main menu showing 4 default pairs

✅ **Success**: User registered in MySQL database!

### Test 2: Log a Trade

1. Send: `/newtrade`
2. Follow prompts to log a complete trade
3. Send: `/opentrades`
4. **Expected**: Your trade appears in the list

✅ **Success**: Trade saved to MySQL!

### Test 3: Persistence Test (CRITICAL)

This tests that data survives redeployments:

1. **Use the bot**: Register, log a trade, add a pair
2. **Go to Railway Dashboard**
3. **Click on your bot service**
4. **Settings → Restart Deployment**
5. Wait for bot to restart (~30 seconds)
6. **Send `/start` in Telegram**
7. **Expected**: "Welcome back! 👋" (NOT setup screen)
8. **Send `/opentrades`**
9. **Expected**: Your trades still there

✅ **SUCCESS**: Data persists across restarts! Problem solved! 🎉

---

## 🗄️ Step 6: Verify Database Tables (Optional)

Want to peek inside your MySQL database?

### Via Railway Dashboard

1. **Click on MySQL service**
2. **Click "Data" tab**
3. You'll see the Query Editor

### Run this query to see your data:

```sql
-- Show all tables
SHOW TABLES;

-- View users
SELECT * FROM users;

-- View trades
SELECT * FROM trades ORDER BY created_at DESC LIMIT 10;

-- View accounts
SELECT * FROM accounts;

-- View pairs
SELECT * FROM pairs;
```

You should see your registered users, trades, accounts, and pairs!

---

## 💰 Pricing Information

### Railway MySQL Costs

**Hobby Plan ($5/month)**:
- ✅ Includes MySQL database
- ✅ 512 MB RAM
- ✅ 1 GB Disk
- ✅ Shared CPU

**For your bot:**
- Estimated database size: ~5 MB/month (very small)
- Your usage will be **well within free tier**
- No extra charges expected

**Cost breakdown:**
- 1000 trades ≈ 0.5 MB
- 100 users ≈ 0.1 MB
- **Total after 1 year: ~50 MB** (plenty of room!)

---

## 🎯 Expected Behavior

### ✅ What Should Work Now

- Users register once and stay registered
- `/start` shows "Welcome back!" for returning users
- All trades persist across bot restarts
- Pairs and accounts saved permanently
- No data loss on Railway redeployments
- Multiple users can use bot simultaneously

### ❌ What Was Broken Before (Now Fixed)

- ~~Users saw setup screen every time~~ ✅ FIXED
- ~~Lost all trades on redeploy~~ ✅ FIXED
- ~~Lost user configurations~~ ✅ FIXED
- ~~CSV files disappeared~~ ✅ FIXED (no more CSV!)

---

## 🔍 Troubleshooting

### Issue: "DATABASE_URL not set in environment variables"

**Cause**: MySQL service not linked to bot

**Solution**:
1. Verify MySQL service exists in your Railway project
2. Both services should be in the **same project**
3. Wait 1-2 minutes for Railway to link them
4. Restart bot deployment if needed

---

### Issue: "Can't connect to MySQL server"

**Cause**: MySQL service still starting or networking issue

**Solution**:
1. Click MySQL service → Check status is "Active"
2. Wait 2-3 minutes for full startup
3. Restart bot deployment after MySQL is active
4. Check Variables tab has `DATABASE_URL`

---

### Issue: "Table doesn't exist"

**Cause**: Database initialization failed

**Solution**:
1. Check deployment logs for errors during table creation
2. Manually create tables via Railway MySQL Data tab:
   - Click MySQL service → Data tab
   - Copy SQL from `database.py` or run: `python database.py` locally
3. Restart bot after tables created

---

### Issue: Bot works but data still resets

**Cause**: Bot connecting to wrong database or local database

**Solution**:
1. Check `DATABASE_URL` environment variable exists in Railway
2. Make sure `.env` file is in `.gitignore`
3. Don't set `DATABASE_URL` in Railway's bot service manually
4. MySQL service handles this automatically

---

### Issue: "Access denied for user"

**Cause**: Database credentials issue

**Solution**:
1. Check `DATABASE_URL` format in MySQL Variables tab
2. Should look like: `mysql://user:password@host:port/database`
3. Delete and recreate MySQL service if corrupted
4. Railway will auto-generate new credentials

---

## 📞 Additional Help

### Check Railway Status

If nothing works, verify Railway platform status:
- https://railway.app/status

### Railway Documentation

- MySQL Setup: https://docs.railway.app/databases/mysql
- Environment Variables: https://docs.railway.app/develop/variables

### Your Bot Logs

Most errors show in deployment logs:
1. Railway Dashboard → Your Bot → Deployments → Latest → Logs

---

## ✨ Success Checklist

Before considering setup complete:

- [ ] MySQL service shows "Active" in Railway
- [ ] `DATABASE_URL` exists in environment
- [ ] Bot deployment logs show "Database initialized"
- [ ] `/start` asks for email (first time)
- [ ] User can complete registration
- [ ] `/newtrade` logs a trade successfully
- [ ] `/opentrades` shows the logged trade
- [ ] Restarted bot (Railway Settings → Restart)
- [ ] After restart, `/start` shows "Welcome back!"
- [ ] After restart, `/opentrades` still shows trades
- [ ] No "data loss" or "setup screen" issues

**✅ All checked? You're done! Database migration successful!** 🎉

---

## 🚀 What's Next?

Your bot is now production-ready with:
- ✅ Persistent MySQL database
- ✅ User registration system
- ✅ Trade logging and tracking
- ✅ News alert system
- ✅ Multi-account support
- ✅ Favorite pairs management

**Enjoy your fully functional Trading Journal bot!** 📊🤖

---

## 📝 Quick Reference

### Important URLs
- **Railway Dashboard**: https://railway.app/dashboard
- **Your Project**: Click on "Telegram-Trade-Journal"
- **MySQL Service**: The "MySQL" card in your project
- **Bot Service**: The main service running your bot

### Key Commands
```bash
# Deploy changes
git add . && git commit -m "message" && git push

# Check if MySQL is running (from Railway MySQL Data tab)
SELECT 1;

# View all tables
SHOW TABLES;

# Count users
SELECT COUNT(*) FROM users;

# View recent trades
SELECT * FROM trades ORDER BY created_at DESC LIMIT 5;
```

### Environment Variables
- `TELEGRAM_BOT_TOKEN`: Your bot token (already set)
- `FCS_API_KEY`: News API key (already set)
- `DATABASE_URL`: Auto-created by Railway MySQL ✅

---

**Last Updated**: After MySQL migration  
**Status**: ✅ Production Ready
