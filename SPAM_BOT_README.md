# 💀 Telegram Spam Bot

A powerful Telegram spam bot with admin controls and user management.

## Features

### 🔥 Spam Commands
- `/spam <user_id> <count> <message>` - Spam specific user (max 100 messages)
- `/groupspam <count> <message>` - Spam current group (max 50 messages)
- `/stop` - Stop all active spam tasks

### 🔐 Admin Commands (Master Only)
- `/users` - List all allowed users
- `/allow <user_id>` - Grant user access to bot
- `/revoke <user_id>` - Remove user access
- `/stats` - View bot statistics

## Setup

1. **Get Bot Token:**
   - Create a new bot with [@BotFather](https://t.me/BotFather)
   - Copy the bot token

2. **Install Dependencies:**
   ```bash
   pip install python-telegram-bot
   ```

3. **Configure Bot:**
   - Open `spam_bot.py`
   - Replace `YOUR_SPAM_BOT_TOKEN_HERE` with your bot token
   - Change `ADMIN_USERNAME` to your Telegram username

4. **Run Bot:**
   ```bash
   python3 spam_bot.py
   ```

## Usage Examples

### For Users (with access):
```
/spam 123456789 50 Hello bro!
/groupspam 20 Check this out!
/stop
```

### For Admin:
```
/allow 987654321
/revoke 987654321
/users
/stats
```

## Security Features

- ✅ Admin-only access control
- ✅ User whitelist system
- ✅ Rate limiting (delays between messages)
- ✅ Maximum message limits
- ✅ Task management and stopping

## Configuration

Edit these variables in `spam_bot.py`:

```python
TOKEN = "YOUR_BOT_TOKEN"
ADMIN_USERNAME = "YourUsername"  # Without @
```

## Rate Limits

- **User Spam:** 0.5 second delay between messages
- **Group Spam:** 1 second delay between messages
- **Max User Spam:** 100 messages
- **Max Group Spam:** 50 messages

## Notes

⚠️ **Warning:** Use responsibly! Spamming can get your bot banned.

💡 **Tip:** Only admin can grant access to other users.

🔒 **Security:** Keep your bot token private!

## Author

💀 **P1yu5h{6_9}**

---

**Disclaimer:** This bot is for educational purposes only. Use at your own risk.
