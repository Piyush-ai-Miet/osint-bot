# 🚀 Deployment Guide - Private Repo

## ⚠️ IMPORTANT: Keep Your Bot Token Safe!

Your bot token is already in the code but will be read from environment variables when deployed.

---

## 📦 Option 1: Render.com (RECOMMENDED - FREE)

### Steps:

1. **Create Private GitHub Repo:**
```bash
cd "piyush api bot"
git init
git add .
git commit -m "Initial commit - OSINT Bot"
git branch -M main
```

2. **Create Private Repo on GitHub:**
   - Go to https://github.com/new
   - Name: `osint-bot` (or any name)
   - ✅ Check "Private"
   - Click "Create repository"

3. **Push Code:**
```bash
git remote add origin https://github.com/YOUR_USERNAME/osint-bot.git
git push -u origin main
```

4. **Deploy on Render:**
   - Go to https://render.com
   - Sign up with GitHub
   - Click "New +" → "Web Service"
   - **Grant access to your private repo**
   - Select your repo
   - Settings:
     - **Name:** osint-bot
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `python3 api.py`
   - **Environment Variables** (Add these):
     - Key: `BOT_TOKEN`
     - Value: `8367270183:AAE1AlWPm1A3ILFulA-OnEFpVP_LkjDomp0`
   - Click "Create Web Service"

✅ **Done! Bot will be online 24/7**

---

## 📦 Option 2: Railway.app (FREE $5/month)

### Steps:

1. **Push to Private GitHub** (same as above)

2. **Deploy on Railway:**
   - Go to https://railway.app
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Grant access to private repo
   - Select your repo
   - **Add Environment Variable:**
     - `BOT_TOKEN` = `8367270183:AAE1AlWPm1A3ILFulA-OnEFpVP_LkjDomp0`
   - Click "Deploy"

✅ **Done!**

---

## 📦 Option 3: Replit (FREE - Easiest)

### Steps:

1. **Go to https://replit.com**
2. Click "Create Repl"
3. Choose "Import from GitHub"
4. **Make repo private on Replit**
5. Or manually upload files:
   - Create new Python Repl
   - Upload `api.py` and `requirements.txt`
6. **Add Secret (Environment Variable):**
   - Click 🔒 "Secrets" in left sidebar
   - Key: `BOT_TOKEN`
   - Value: `8367270183:AAE1AlWPm1A3ILFulA-OnEFpVP_LkjDomp0`
7. Click "Run"

⚠️ **Keep Alive:** Replit sleeps after inactivity
- Use https://uptimerobot.com to ping your repl every 5 minutes
- Or use Replit's "Always On" feature (paid)

---

## 📦 Option 4: PythonAnywhere (FREE)

### Steps:

1. **Create account:** https://www.pythonanywhere.com
2. **Upload files:**
   - Go to "Files" tab
   - Upload `api.py` and `requirements.txt`
3. **Install dependencies:**
   - Open Bash console
   - Run: `pip3 install -r requirements.txt`
4. **Run bot:**
   - Go to "Tasks" tab
   - Add scheduled task: `python3 /home/YOUR_USERNAME/api.py`
   - Set to run daily (it will keep running)

---

## 🔒 Security Tips

1. ✅ **Never commit .env file** (already in .gitignore)
2. ✅ **Use environment variables** (already configured)
3. ✅ **Keep repo private** on GitHub
4. ✅ **Regenerate token** if accidentally exposed
5. ✅ **Don't share bot token** with anyone

---

## 🎯 Recommended: Render.com

**Why?**
- ✅ FREE forever (750 hours/month)
- ✅ Works with private repos
- ✅ Auto-deploy on git push
- ✅ Environment variables support
- ✅ 24/7 uptime
- ✅ No credit card needed

---

## 📝 Quick Commands

### Update Bot (after changes):
```bash
git add .
git commit -m "Updated bot"
git push
```
Render will auto-deploy! 🚀

### Check if bot is running:
Send `/start` to your bot on Telegram

---

## 🆘 Troubleshooting

**Bot not responding?**
1. Check Render logs
2. Verify BOT_TOKEN is correct
3. Make sure bot is not stopped

**Deployment failed?**
1. Check requirements.txt
2. Verify Python version (3.9+)
3. Check Render build logs

---

## 💀 BLACKHAT COMRADE
**by P1yu5h69** 🔥
