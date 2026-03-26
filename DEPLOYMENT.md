# 🚀 Deployment Guide

## Quick Deploy Options

### Option 0: Any Hosting via Docker (Most Reliable)
Use this if buildpacks fail (like the Python runtime download error you saw).

1. Ensure your host deploys from the root `Dockerfile`
2. Set environment variables:
   - `TELEGRAM_BOT_TOKEN` (required)
   - `FCS_API_KEY` (optional)
   - `START_MODE` (optional, defaults to `both`)
3. Expose port `8080` (or let host inject `PORT` automatically)

`START_MODE` values:
- `both`: runs bot + dashboard web server in one container
- `web`: runs dashboard API/web only
- `bot`: runs Telegram bot only

This project now includes:
- root `Dockerfile` (builds React dashboard + Python app)
- `.python-version` for non-Docker Python hosts

### Universal Deployment Model (Any Platform)
Use one of these patterns depending on what your host supports:

1. Single service, single process:
   - Command: `python start.py both`
   - Use when one container/service should run bot + dashboard together.

2. Two services (recommended at scale):
   - Web service command: `python start.py web`
   - Worker service command: `python start.py bot`
   - Use when your host supports separate web + worker processes.

3. Procfile-based hosts:
   - `Procfile` now defines both `web` and `worker` process types.
   - Scale what you need on the target platform.

For buildpack Python hosts, this repo now uses `.python-version` (3.11) instead of the deprecated `runtime.txt`.

### Option 1: Railway.app (Easiest - $5/month)
1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. Sign in with GitHub
4. New Project → Deploy from GitHub repo
5. Select `Telegram-Trade-Journal`
6. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `FCS_API_KEY` (optional)
7. **IMPORTANT - Add Persistent Volume:**
   - Click on your service
   - Go to "Data" tab
   - Click "Add Volume"
   - Mount Path: `/app/data`
   - This ensures user data persists between deployments
8. Deploy!

### Option 2: Render.com (Free Tier Available)
1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. New → Background Worker
4. Connect GitHub repo
5. Add environment variables
6. Deploy!

### Option 3: VPS (DigitalOcean, Linode, etc.)
See detailed instructions below.

---

## 📋 Initial Server Setup (VPS)

### Prerequisites
- Ubuntu 22.04+ server
- SSH access
- Python 3.10+

### Step 1: Clone Repository
```bash
ssh user@your-server-ip
cd ~
git clone https://github.com/aoiyiola/Telegram-Trade-Journal.git
cd Telegram-Trade-Journal
```

### Step 2: Create Environment File
```bash
nano .env
```

Add your credentials:
```env
TELEGRAM_BOT_TOKEN=your_actual_bot_token_from_botfather
FCS_API_KEY=your_fcs_api_key_or_leave_empty
```

Save: `Ctrl+X`, then `Y`, then `Enter`

### Step 3: Install Dependencies
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 4: Test Run
```bash
python bot.py
```

Bot should start! Press `Ctrl+C` to stop.

### Step 5: Run as Service (Auto-restart)
```bash
sudo nano /etc/systemd/system/trading-bot.service
```

Paste this content (adjust paths):
```ini
[Unit]
Description=Telegram Trading Journal Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/Telegram-Trade-Journal
Environment="PATH=/home/YOUR_USERNAME/Telegram-Trade-Journal/.venv/bin"
ExecStart=/home/YOUR_USERNAME/Telegram-Trade-Journal/.venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Replace `YOUR_USERNAME` with your actual username (run `whoami` to check).

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
```

Check status:
```bash
sudo systemctl status trading-bot
```

View logs:
```bash
sudo journalctl -u trading-bot -f
```

---

## 🔄 Deploying Updates

When you add new features:

```bash
# 1. Push code from local/codespace
git add .
git commit -m "Add new feature"
git push origin main

# 2. Pull on server
ssh user@your-server
cd ~/Telegram-Trade-Journal
git pull origin main

# 3. Install any new dependencies
source .venv/bin/activate
pip install -r requirements.txt

# 4. Restart bot
sudo systemctl restart trading-bot

# 5. Verify it's running
sudo systemctl status trading-bot
```

---

## 🛠️ Useful Commands

### Check bot status
```bash
sudo systemctl status trading-bot
```

### View live logs
```bash
sudo journalctl -u trading-bot -f
```

### Restart bot
```bash
sudo systemctl restart trading-bot
```

### Stop bot
```bash
sudo systemctl stop trading-bot
```

### Start bot manually (for debugging)
```bash
cd ~/Telegram-Trade-Journal
source .venv/bin/activate
python bot.py
```

---

## 🔒 Security Checklist

- ✅ `.env` file created on server only (not in git)
- ✅ `.gitignore` prevents sensitive files from being committed
- ✅ `data/` folder stays on server (user privacy)
- ✅ Bot token kept secret
- ✅ Server firewall configured (only SSH and bot traffic)

---

## 📊 Data Backup

User data is stored in:
```
data/
  └── user_{telegram_id}/
      ├── global.csv
      ├── account_main.csv
      └── account_*.csv

user_data/
  └── user_{telegram_id}_config.json
```

**Backup command:**
```bash
# Create backup
cd ~/Telegram-Trade-Journal
tar -czf backup-$(date +%Y%m%d).tar.gz data/ user_data/

# Download to local machine
scp user@server:~/Telegram-Trade-Journal/backup-*.tar.gz ./
```

---

## 🆘 Troubleshooting

### Bot not responding
```bash
sudo systemctl status trading-bot
sudo journalctl -u trading-bot -n 50
```

### Check if bot token is valid
```bash
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

### Multiple instances conflict
```bash
pkill -9 -f bot.py
sudo systemctl restart trading-bot
```

### Permission errors
```bash
sudo chown -R $USER:$USER ~/Telegram-Trade-Journal
chmod +x bot.py
```

---

## 📞 Support

- Bot Issues: Check logs with `journalctl -u trading-bot -f`
- Telegram API: https://core.telegram.org/bots
- FCS API: https://fcsapi.com/document

---

## ✅ Post-Deployment Testing

1. Send `/start` to your bot
2. Create an account
3. Add a trading pair
4. Log a test trade with `/newtrade`
5. View trades with `/opentrades`
6. Test news alerts with `/news`

All working? You're live! 🎉
