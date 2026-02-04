import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

# Bot Configuration
TOKEN = os.getenv("SPAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("SPAM_BOT_TOKEN environment variable not set!")
    
ADMIN_USERNAME = "Piyushhu"

# Storage
allowed_users = set()  # Users who can use the bot
spam_tasks = {}  # Active spam tasks

# Admin Commands

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = (
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║   💀 SPAM BOT ACTIVATED 💀    ║\n"
        "║      by P1yu5h{6_9}           ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        "🔥 **SPAM COMMANDS**\n\n"
        "`/spam <user_id> <count> <message>` - Spam user\n"
        "`/groupspam <count> <message>` - Spam current group\n"
        "`/stop` - Stop all spam tasks\n"
    )
    
    if user.username == ADMIN_USERNAME:
        msg += (
            "\n```\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "```\n"
            "🔐 **ADMIN COMMANDS**\n\n"
            "`/users` - List all allowed users\n"
            "`/allow <user_id>` - Allow user access\n"
            "`/revoke <user_id>` - Revoke user access\n"
            "`/stats` - Bot statistics\n\n"
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   💀 MASTER ACCESS ACTIVE 💀  ║\n"
            "╚═══════════════════════════════╝\n"
            "```"
        )
    
    await update.message.reply_text(msg, parse_mode='Markdown')


async def spam_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Check if user is admin or allowed
    if username != ADMIN_USERNAME and user_id not in allowed_users:
        await update.message.reply_text(
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   ❌ ACCESS DENIED ❌         ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            "🚫 You don't have permission to use this bot\n"
            f"💡 Contact @{ADMIN_USERNAME} for access",
            parse_mode='Markdown'
        )
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "⚠️ **USAGE:**\n"
            "`/spam <user_id> <count> <message>`\n\n"
            "**Example:**\n"
            "`/spam 123456789 50 Hello bro!`",
            parse_mode='Markdown'
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        count = int(context.args[1])
        message = ' '.join(context.args[2:])
        
        if count > 100:
            await update.message.reply_text("⚠️ Maximum 100 messages allowed per spam!")
            return
        
        await update.message.reply_text(
            f"```\n⏳ INITIATING SPAM...\n```\n"
            f"🎯 Target: {target_user_id}\n"
            f"📊 Count: {count}\n"
            f"💬 Message: {message[:50]}...",
            parse_mode='Markdown'
        )
        
        # Start spamming
        task_id = f"{user_id}_{target_user_id}"
        spam_tasks[task_id] = True
        
        success = 0
        failed = 0
        
        for i in range(count):
            if task_id not in spam_tasks:
                break
            
            try:
                await context.bot.send_message(chat_id=target_user_id, text=message)
                success += 1
                await asyncio.sleep(0.5)  # Delay to avoid rate limit
            except Exception as e:
                failed += 1
        
        if task_id in spam_tasks:
            del spam_tasks[task_id]
        
        await update.message.reply_text(
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   ✅ SPAM COMPLETED ✅        ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            f"✅ Sent: {success}\n"
            f"❌ Failed: {failed}",
            parse_mode='Markdown'
        )
        
    except ValueError:
        await update.message.reply_text("❌ Invalid user_id or count!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def group_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    chat_id = update.effective_chat.id
    
    # Check if user is admin or allowed
    if username != ADMIN_USERNAME and user_id not in allowed_users:
        await update.message.reply_text("❌ Access denied!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ **USAGE:**\n"
            "`/groupspam <count> <message>`\n\n"
            "**Example:**\n"
            "`/groupspam 20 Hello everyone!`",
            parse_mode='Markdown'
        )
        return
    
    try:
        count = int(context.args[0])
        message = ' '.join(context.args[1:])
        
        if count > 50:
            await update.message.reply_text("⚠️ Maximum 50 messages allowed for group spam!")
            return
        
        await update.message.reply_text(
            f"```\n⏳ INITIATING GROUP SPAM...\n```\n"
            f"📊 Count: {count}\n"
            f"💬 Message: {message[:50]}...",
            parse_mode='Markdown'
        )
        
        # Start spamming
        task_id = f"group_{chat_id}"
        spam_tasks[task_id] = True
        
        success = 0
        
        for i in range(count):
            if task_id not in spam_tasks:
                break
            
            try:
                await context.bot.send_message(chat_id=chat_id, text=message)
                success += 1
                await asyncio.sleep(1)  # Longer delay for groups
            except:
                break
        
        if task_id in spam_tasks:
            del spam_tasks[task_id]
        
        await update.message.reply_text(
            f"```\n✅ SPAM COMPLETED ✅\n```\n"
            f"✅ Sent: {success} messages",
            parse_mode='Markdown'
        )
        
    except ValueError:
        await update.message.reply_text("❌ Invalid count!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def stop_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if username != ADMIN_USERNAME and user_id not in allowed_users:
        await update.message.reply_text("❌ Access denied!")
        return
    
    spam_tasks.clear()
    await update.message.reply_text(
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║   🛑 ALL SPAM STOPPED 🛑      ║\n"
        "╚═══════════════════════════════╝\n"
        "```",
        parse_mode='Markdown'
    )


# Admin Commands

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    
    if username != ADMIN_USERNAME:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if not allowed_users:
        await update.message.reply_text("📋 No users allowed yet!")
        return
    
    user_list = "\n".join([f"• {uid}" for uid in allowed_users])
    await update.message.reply_text(
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║   👥 ALLOWED USERS 👥         ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        f"**Total Users:** {len(allowed_users)}\n\n"
        f"{user_list}",
        parse_mode='Markdown'
    )


async def allow_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    
    if username != ADMIN_USERNAME:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ **USAGE:** `/allow <user_id>`\n\n"
            "**Example:** `/allow 123456789`",
            parse_mode='Markdown'
        )
        return
    
    try:
        user_id = int(context.args[0])
        allowed_users.add(user_id)
        
        await update.message.reply_text(
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   ✅ USER ALLOWED ✅          ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            f"👤 User ID: {user_id}\n"
            f"✅ Access granted!",
            parse_mode='Markdown'
        )
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")


async def revoke_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    
    if username != ADMIN_USERNAME:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ **USAGE:** `/revoke <user_id>`\n\n"
            "**Example:** `/revoke 123456789`",
            parse_mode='Markdown'
        )
        return
    
    try:
        user_id = int(context.args[0])
        if user_id in allowed_users:
            allowed_users.remove(user_id)
            await update.message.reply_text(
                "```\n"
                "╔═══════════════════════════════╗\n"
                "║   ✅ ACCESS REVOKED ✅        ║\n"
                "╚═══════════════════════════════╝\n"
                "```\n"
                f"👤 User ID: {user_id}\n"
                f"❌ Access removed!",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("⚠️ User not in allowed list!")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    
    if username != ADMIN_USERNAME:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    await update.message.reply_text(
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║   📊 BOT STATISTICS 📊        ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        f"👥 **Allowed Users:** {len(allowed_users)}\n"
        f"🔥 **Active Spam Tasks:** {len(spam_tasks)}\n\n"
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║   💀 by P1yu5h{6_9} 💀        ║\n"
        "╚═══════════════════════════════╝\n"
        "```",
        parse_mode='Markdown'
    )


if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    # User commands
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('spam', spam_user))
    app.add_handler(CommandHandler('groupspam', group_spam))
    app.add_handler(CommandHandler('stop', stop_spam))
    
    # Admin commands
    app.add_handler(CommandHandler('users', list_users))
    app.add_handler(CommandHandler('allow', allow_user))
    app.add_handler(CommandHandler('revoke', revoke_user))
    app.add_handler(CommandHandler('stats', stats))
    
    print("💀 Spam Bot Started! 💀")
    app.run_polling(drop_pending_updates=True)
