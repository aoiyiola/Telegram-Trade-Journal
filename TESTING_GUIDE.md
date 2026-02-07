# Pre-Deployment Testing Guide

## 🧪 Complete Testing Checklist

Test all functionality locally before deploying to Railway.

## Prerequisites

1. **Install MySQL locally** (for testing):
   ```bash
   # On Ubuntu/Debian
   sudo apt update
   sudo apt install mysql-server
   sudo systemctl start mysql
   
   # On Mac
   brew install mysql
   brew services start mysql
   ```

2. **Create local test database**:
   ```bash
   # Connect to MySQL as root
   mysql -u root -p
   
   # Create database
   CREATE DATABASE trade_journal_test;
   
   # Create user (optional)
   CREATE USER 'tradebot'@'localhost' IDENTIFIED BY 'test123';
   GRANT ALL PRIVILEGES ON trade_journal_test.* TO 'tradebot'@'localhost';
   FLUSH PRIVILEGES;
   
   # Exit
   exit;
   ```

3. **Set DATABASE_URL locally**:
   ```bash
   # Add to .env file
   DATABASE_URL=mysql://root@localhost/trade_journal_test
   
   # Or if you created a user:
   DATABASE_URL=mysql://tradebot:test123@localhost/trade_journal_test
   ```

4. **Install mysql-connector**:
   ```bash
   pip install mysql-connector-python==8.3.0
   ```

## 🔧 Test 1: Database Connection

**Test**: Verify bot can connect to database

```bash
python bot.py
```

**Expected Output**:
```
✅ Database initialized successfully
✅ Database tables created
✅ News cache initialized successfully
🚀 Trading Journal Bot is starting...
```

**If you see errors**:
- Check DATABASE_URL is correct
- Verify MySQL is running: `sudo systemctl status mysql` (Linux) or `brew services list` (Mac)
- Confirm database exists: `mysql -u root -p -e "SHOW DATABASES;"`

---

## 👤 Test 2: New User Registration

**Test**: First-time user flow

1. Start bot: `/start`
2. **Expected**: "Welcome! Please provide your email"
3. Send email: `test@example.com`
4. **Expected**: "Please enter your first account name"
5. Send account name: `Demo Account`
6. **Expected**: Main menu with 4 default pairs

**Verify**:
- User stored in database
- Default account created
- Default pairs available
- No errors in console

**Check database**:
```bash
mysql -u root -p trade_journal_test

SELECT * FROM users;
SELECT * FROM accounts;
SELECT * FROM pairs;
```

---

## 🔄 Test 3: Existing User (Persistence Test)

**Test**: User doesn't see setup again

1. **Stop bot** (Ctrl+C)
2. **Restart bot**: `python bot.py`
3. Send `/start` again
4. **Expected**: "Welcome back! 👋" (NOT setup screen)

**This is THE critical test!**  
If this fails, persistence isn't working.

---

## 📊 Test 4: Trade Logging

**Test**: Complete trade logging flow

1. `/newtrade`
2. **Expected**: Account selection (should show "Demo Account")
3. Select account
4. **Expected**: Pair selection (4 default pairs)
5. Select pair (e.g., EURUSD)
6. **Expected**: Direction selection
7. Select direction (BUY/SELL)
8. **Expected**: "Enter entry price"
9. Enter: `1.0850`
10. **Expected**: "Enter stop loss"
11. Enter: `1.0800`
12. **Expected**: "Enter take profit"
13. Enter: `1.0900`
14. **Expected**: "Any notes?"
15. Skip notes
16. **Expected**: "✅ Trade Logged Successfully!" with trade ID

**Verify**:
- Trade has ID like T1, T2, etc.
- Entry, SL, TP correct
- Session detected (London/NY/Asian/Off)
- Status shows OPEN

**Check database**:
```sql
SELECT * FROM trades;
```

---

## 📋 Test 5: Open Trades Query

**Test**: View open trades

1. `/opentrades`
2. **Expected**: List showing the trade you just logged
3. **Verify**: 
   - Trade ID matches
   - Pair, direction, prices correct
   - Account name shown
   - Session displayed

---

## 📜 Test 6: Recent Trades Query

**Test**: View recent trades history

1. `/recenttrades`
2. **Expected**: List showing all recent trades
3. **Verify**: Shows the logged trade with all details

---

## ✏️ Test 7: Update Trade

**Test**: Close a trade with result

1. `/updatetrade`
2. **Expected**: List of open trades with buttons
3. Click on your trade
4. **Expected**: Result selection (Win/Loss/BE)
5. Select "Win"
6. **Expected**: "✅ Trade Updated Successfully!"
7. **Verify**: 
   - Status changed to CLOSED
   - Result shows "W"

**Check database**:
```sql
SELECT * FROM trades WHERE result IS NOT NULL;
```

---

## 💱 Test 8: Manage Pairs

**Test**: Add custom pair

1. `/managepairs`
2. **Expected**: List of current pairs (4 defaults)
3. Select "➕ Add New Pair"
4. Send: `BTCUSD`
5. **Expected**: "✅ Pair BTCUSD added!"
6. `/managepairs` again
7. **Verify**: BTCUSD now in list

**Test**: Remove pair

1. `/managepairs`
2. Select pair to remove (e.g., USDJPY)
3. Confirm removal
4. **Expected**: "✅ Pair removed!"
5. **Verify**: Pair no longer in list

**Check persistence**:
1. Restart bot
2. `/managepairs`
3. **Verify**: BTCUSD still there, USDJPY still gone

---

## 💼 Test 9: Manage Accounts

**Test**: Add second account

1. `/manageaccounts`
2. **Expected**: Shows "Demo Account" (default)
3. Select "➕ Add New Account"
4. Send: `Live Account`
5. **Expected**: "✅ Account 'Live Account' created!"
6. `/manageaccounts` again
7. **Verify**: Both accounts listed

**Test**: Set default account

1. In accounts list, select "Live Account"
2. Select "⭐ Set as Default"
3. **Expected**: "✅ Live Account is now your default"
4. `/newtrade`
5. **Verify**: "Live Account" selected by default

**Test**: Rename account

1. `/manageaccounts`
2. Select account
3. Select "✏️ Rename"
4. Send new name: `Production Account`
5. **Verify**: Name updated

---

## 📰 Test 10: News System (Should Still Work)

**Test**: News cache still uses JSON file

1. `/news`
2. **Expected**: Shows upcoming news events (if FCS API key set)
3. **Verify**: No database errors
4. **Check**: `data/news_cache.json` file exists and updates

---

## 🔄 Test 11: Full Persistence Test (CRITICAL)

**This simulates Railway redeploy**

1. **Use bot** - create trades, add pairs, add accounts
2. **Stop bot** - Ctrl+C
3. **Delete database and recreate**:
   ```bash
   mysql -u root -p
   DROP DATABASE trade_journal_test;
   CREATE DATABASE trade_journal_test;
   exit;
   ```
4. **Restart bot** - `python bot.py`
5. `/start`
6. **Expected**: Setup screen (because database is empty)
7. **Complete setup** - register as new user
8. **Log some trades**
9. **Stop bot** again
10. **Restart bot** (without dropping database)
11. `/start`
12. **Expected**: "Welcome back!" ✅
13. **Verify all data** still there:
    - `/opentrades` - shows trades
    - `/managepairs` - shows pairs
    - `/manageaccounts` - shows accounts

**If this passes: Database persistence is working! 🎉**

---

## 🐛 Common Issues & Solutions

### "DATABASE_URL not set in environment variables"
- **Fix**: Add to `.env` file
- Format: `DATABASE_URL=mysql://root@localhost/trade_journal_test`

### "Module 'mysql.connector' not found"
- **Fix**: `pip install mysql-connector-python==8.3.0`

### "Connection refused"
- **Fix**: Start MySQL service
- Ubuntu: `sudo systemctl start mysql`
- Mac: `brew services start mysql`

### "Database 'trade_journal_test' does not exist"
- **Fix**: Create it:
  ```bash
  mysql -u root -p -e "CREATE DATABASE trade_journal_test;"
  ```

### User sees setup screen every time
- **Problem**: Database not persisting
- **Check**: Is DATABASE_URL correct?
- **Verify**: Can you query the database directly?
  ```bash
  mysql -u root -p trade_journal_test -e "SELECT * FROM users;"
  ```

### Trades not showing in /opentrades
- **Check database directly**:
  ```sql
  SELECT * FROM trades WHERE status = 'OPEN';
  ```
- **Verify**: telegram_id matches your Telegram ID

---

## ✅ Pre-Deployment Checklist

Before pushing to Railway:

- [ ] Database connection works locally
- [ ] Tables created automatically
- [ ] New user registration works
- [ ] User sees "Welcome back" after restart
- [ ] Trade logging saves to database
- [ ] Open trades query works
- [ ] Recent trades query works
- [ ] Update trade works
- [ ] Manage pairs persists changes
- [ ] Manage accounts persists changes
- [ ] Full restart preserves all data
- [ ] News system still works
- [ ] No console errors during testing

**If ALL tests pass: Ready to deploy! 🚀**

---

## 🚀 Railway Deployment Steps

After all tests pass:

1. **Commit changes**:
   ```bash
   git add .
   git commit -m "Migrate to MySQL database"
   git push
   ```

2. **Add MySQL on Railway**:
   - Railway Dashboard → Project → "+ New" → Database → MySQL

3. **Wait for deployment** (~2-3 minutes)

4. **Check Railway logs**:
   - Should see: "✅ Database initialized successfully"

5. **Test on Railway**:
   - Talk to your bot on Telegram
   - Run through Test 2 (new user)
   - Run through Test 11 (persistence)

6. **Monitor for issues**:
   - Check Railway logs for errors
   - Test all commands work
   - Verify data persists after Railway restart

---

## 📊 Success Criteria

✅ **Bot starts** without errors  
✅ **Database tables** created automatically  
✅ **Users register** successfully  
✅ **Trades save** to database  
✅ **Queries return** correct data  
✅ **Updates modify** database correctly  
✅ **Data persists** across restarts  
✅ **No CSV/JSON** file errors  
✅ **Railway deployment** completes successfully  
✅ **Production bot** works identically to local  

**When all criteria met: Migration is successful! 🎉**
