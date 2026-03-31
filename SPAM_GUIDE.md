# 💀 Spam Commands Guide

## How to Use Spam Commands

### 1️⃣ Spam a User (DM)

**Command:**
```
/spam <user_id> <count> <message>
```

**Example:**
```
/spam 123456789 50 Hello bro! How are you?
```

**What happens:**
- Spam bot will send "Hello bro! How are you?" 50 times to user ID 123456789
- Messages sent via separate spam bot (not your main OSINT bot)
- Max 100 messages allowed

---

### 2️⃣ Spam a Group

**Command:**
```
/groupspam <count> <message>
```

**Example:**
```
/groupspam 20 Join our channel @example
```

**What happens:**
- Spam bot will send the message 20 times in the CURRENT group
- Max 50 messages allowed for groups

---

### 3️⃣ Stop All Spam

**Command:**
```
/stopspam
```

**What happens:**
- Stops all active spam tasks immediately

---

## 🔐 Admin Commands (Only You)

### Allow Someone to Use Spam

**Command:**
```
/allowspam <user_id>
```

**Example:**
```
/allowspam 987654321
```

**What happens:**
- User 987654321 can now use spam commands

---

### Revoke Spam Access

**Command:**
```
/revokespam <user_id>
```

**Example:**
```
/revokespam 987654321
```

---

### List Allowed Users

**Command:**
```
/spamusers
```

**What happens:**
- Shows list of all users who can use spam commands

---

## 📋 How to Get User ID

**Method 1:** Forward a message from the user to [@userinfobot](https://t.me/userinfobot)

**Method 2:** Use [@getidsbot](https://t.me/getidsbot)

**Method 3:** Ask them to send `/start` to your bot, check logs

---

## ⚠️ Important Notes

- Only YOU (Piyushhu) and allowed users can spam
- Spam bot uses separate token (not OSINT bot)
- Rate limits: 0.5s delay between messages
- Max limits: 100 (user), 50 (group)
- Messages sent from spam bot account

---

## 💀 by P1yu5h{6_9}
