import requests
import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# Get token from environment variable (for security)
TOKEN = os.getenv("BOT_TOKEN")
SPAM_BOT_TOKEN = os.getenv("SPAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")
if not SPAM_BOT_TOKEN:
    raise ValueError("SPAM_BOT_TOKEN environment variable not set!")

ADMIN_USERNAME = "Piyushhu"
FREE_GROUPS = []  # List of group IDs where bot is free

# Restricted numbers (Master's numbers - DO NOT SEARCH)
RESTRICTED_NUMBERS = [
    "7505426304", 
    "8791199014"
]

# Spam bot storage
allowed_spam_users = set()  # Users who can use spam commands
spam_tasks = {}  # Active spam tasks

# User tracking and logs
bot_users = set()  # All users who have used the bot
user_logs = []  # Command logs: {user_id, username, command, timestamp}
blocked_users = set()  # Users who are blocked from using bot

# Credits storage (in production, use a database)
user_credits = {}

# API URLs storage (can be changed by admin)
API_URLS = {
    'num': 'https://osint-num-info.gauravcyber0.workers.dev/?mobile=',
    'vehicle': 'https://prosnal-vehicle.gauravcyber0.workers.dev/?vehicle=',
    'pincode': 'https://pin-code-info.gauravcyber0.workers.dev/?pincode=',
    'ifsc': 'https://ifsc-code-info.gauravcyber0.workers.dev/?ifsc=',
    'ip': 'http://ip-api.com/json/',
    'gmail': 'https://gmail-info-api-two.vercel.app/info?mail=',
    'imei': 'https://imei-number-infoo.vercel.app/api/imei?imei=',
    'bomber': 'https://bomm.gauravcyber0.workers.dev/?phone=',
    'ai_blackbox': 'https://delicate-field-68bd.rasiksarkarrasiksarkar.workers.dev/?question=',
    'ai_gemini': 'https://delicate-field-68bd.rasiksarkarrasiksarkar.workers.dev/?question=',
    'ai_chatgpt': 'https://delicate-field-68bd.rasiksarkarrasiksarkar.workers.dev/?question='
}

# Simple HTTP server for health check
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<html><body><h1>Bot is running!</h1></body></html>')
    
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass

def run_server():
    port = int(os.getenv('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()


def is_free_group(chat_id):
    """Check if the chat is a free group"""
    return chat_id in FREE_GROUPS


def log_command(user_id, username, command, details=""):
    """Log user commands"""
    from datetime import datetime
    log_entry = {
        'user_id': user_id,
        'username': username or "Unknown",
        'command': command,
        'details': details,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    user_logs.append(log_entry)
    bot_users.add(user_id)
    
    # Keep only last 100 logs
    if len(user_logs) > 100:
        user_logs.pop(0)


def is_user_blocked(user_id):
    """Check if user is blocked"""
    return user_id in blocked_users


def get_credits(user_id):
    """Get user credits, initialize with 10 if new user"""
    if user_id not in user_credits:
        user_credits[user_id] = 10
    return user_credits[user_id]


def deduct_credit(user_id, chat_id):
    """Deduct 1 credit from user if not in free group"""
    if is_free_group(chat_id):
        return True  # Free group, no deduction
    
    if user_id not in user_credits:
        user_credits[user_id] = 10
    if user_credits[user_id] > 0:
        user_credits[user_id] -= 1
        return True
    return False


def add_credits(user_id, amount):
    """Add credits to user (admin only)"""
    if user_id not in user_credits:
        user_credits[user_id] = 0
    user_credits[user_id] += amount


def add_free_group(chat_id):
    """Add a group to free list"""
    if chat_id not in FREE_GROUPS:
        FREE_GROUPS.append(chat_id)
        return True
    return False


def remove_free_group(chat_id):
    """Remove a group from free list"""
    if chat_id in FREE_GROUPS:
        FREE_GROUPS.remove(chat_id)
        return True
    return False


def format_json_response(data):
    """Format JSON response into readable text with better structure"""
    
    def escape_markdown(text):
        """Escape markdown special characters"""
        if not text:
            return text
        # Escape special markdown characters
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        text = str(text)
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    try:
        if isinstance(data, str):
            # Try to parse JSON, handle empty or invalid responses
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return (
                    "```\n"
                    "╔═══════════════════════════════╗\n"
                    "║   🔧 UNDER MAINTENANCE 🔧    ║\n"
                    "╚═══════════════════════════════╝\n"
                    "```\n"
                    "⚠️ Invalid response from API\n"
                    "🔄 Please try again later"
                )
        
        # Check if data is empty or None
        if not data:
            return (
                "```\n"
                "╔═══════════════════════════════╗\n"
                "║   🔧 UNDER MAINTENANCE 🔧    ║\n"
                "╚═══════════════════════════════╝\n"
                "```\n"
                "⚠️ No data received from API\n"
                "🔄 Please try again later"
            )
        
        # Mask all seller/api_sell fields recursively
        def mask_seller_fields(obj):
            if isinstance(obj, dict):
                for key in list(obj.keys()):
                    if key in ['seller', 'api_sell', 'api_seller']:
                        obj[key] = "*** **** ** :- @***********"
                    elif key == '@Gauravcyber_op':
                        obj['@****_****'] = obj.pop(key)
                        mask_seller_fields(obj['@****_****'])
                    else:
                        mask_seller_fields(obj[key])
            elif isinstance(obj, list):
                for item in obj:
                    mask_seller_fields(item)
        
        mask_seller_fields(data)
        
        formatted = "```\n"
        formatted += "╔═══════════════════════════════╗\n"
        formatted += "║  ⚡ OSINT DATA EXTRACTED ⚡   ║\n"
        formatted += "╚═══════════════════════════════╝\n"
        formatted += "```\n"
        
        # Handle the specific API structure
        if 'data' in data and isinstance(data['data'], dict):
            api_data = data['data']
            
            # Process api_1 section (main info)
            if 'api_1' in api_data:
                formatted += "\n```\n━━━━━━━ 📱 MAIN INFO ━━━━━━━\n```\n"
                for key, value in api_data['api_1'].items():
                    if value and str(value).strip() and value != 'N/A':
                        key_clean = key.replace('_', ' ')
                        formatted += f"• **{key_clean}:** {value}\n"
            
            # Process @****_**** section (detailed records) - masked name
            if '@****_****' in api_data:
                masked_data = api_data['@****_****']
                if 'result' in masked_data and isinstance(masked_data['result'], list):
                    results = masked_data['result']
                    
                    # Remove duplicates based on mobile+name
                    seen = set()
                    unique_results = []
                    for item in results:
                        key = f"{item.get('mobile', '')}-{item.get('name', '')}"
                        if key not in seen:
                            seen.add(key)
                            unique_results.append(item)
                    
                    formatted += f"\n```\n━━━━━━━ 📋 RECORDS ({len(unique_results)}) ━━━━━━━\n```\n"
                    
                    for idx, result in enumerate(unique_results[:2], 1):
                        formatted += f"\n**RECORD #{idx}**\n"
                        
                        if result.get('name'):
                            formatted += f"👤 Name: {result['name']}\n"
                        
                        if result.get('father_name'):
                            formatted += f"👨 Father: {result['father_name']}\n"
                        
                        if result.get('mobile'):
                            formatted += f"📱 Mobile: {result['mobile']}\n"
                        
                        if result.get('alt_mobile') and result['alt_mobile'] not in ['', 'N/A']:
                            formatted += f"📞 Alt: {result['alt_mobile']}\n"
                        
                        if result.get('email') and result['email'] not in ['', 'N/A']:
                            formatted += f"📧 Email: {result['email']}\n"
                        
                        if result.get('circle'):
                            formatted += f"🌐 Circle: {result['circle']}\n"
                        
                        if result.get('address'):
                            addr = result['address'].replace('!', ', ')[:100]
                            formatted += f"📍 Address: {addr}...\n"
                        
                        if result.get('id_number'):
                            formatted += f"🆔 ID: {result['id_number']}\n"
                        
                        formatted += "\n"
                    
                    if len(unique_results) > 2:
                        formatted += f"_...and {len(unique_results) - 2} more records_\n"
            
            # VEHICLE API - has rc_number key
            elif 'rc_number' in api_data:
                vdata = api_data
                formatted += "\n```\n━━━━━━━ 🚗 VEHICLE INFO ━━━━━━━\n```\n"
                
                if vdata.get('rc_number'):
                    formatted += f"🚗 **RC Number:** {vdata['rc_number']}\n"
                if vdata.get('owner_name'):
                    formatted += f"👤 **Owner:** {vdata['owner_name']}\n"
                if vdata.get('father_name') and vdata['father_name']:
                    formatted += f"👨 **Father:** {vdata['father_name']}\n"
                if vdata.get('mobile_number') and vdata['mobile_number']:
                    formatted += f"📱 **Mobile:** {vdata['mobile_number']}\n"
                if vdata.get('present_address'):
                    formatted += f"📍 **Address:** {vdata['present_address']}\n"
                
                formatted += f"\n```\n━━━━━━━ 🚙 DETAILS ━━━━━━━\n```\n"
                
                if vdata.get('maker_description'):
                    formatted += f"🏭 **Maker:** {vdata['maker_description']}\n"
                if vdata.get('maker_model'):
                    formatted += f"🚙 **Model:** {vdata['maker_model']}\n"
                if vdata.get('body_type'):
                    formatted += f"🔧 **Type:** {vdata['body_type']}\n"
                if vdata.get('fuel_type'):
                    formatted += f"⛽ **Fuel:** {vdata['fuel_type']}\n"
                if vdata.get('color'):
                    formatted += f"🎨 **Color:** {vdata['color']}\n"
                if vdata.get('manufacturing_date'):
                    formatted += f"📅 **Mfg:** {vdata['manufacturing_date']}\n"
                if vdata.get('registration_date'):
                    formatted += f"📝 **Reg:** {vdata['registration_date']}\n"
                
                formatted += f"\n```\n━━━━━━━ 📋 REGISTRATION ━━━━━━━\n```\n"
                
                if vdata.get('registered_at'):
                    formatted += f"📍 **RTO:** {vdata['registered_at']}\n"
                if vdata.get('rc_status'):
                    formatted += f"✅ **Status:** {vdata['rc_status']}\n"
                if vdata.get('fit_up_to'):
                    formatted += f"🔧 **Fitness:** {vdata['fit_up_to']}\n"
                if vdata.get('tax_upto'):
                    formatted += f"💰 **Tax:** {vdata['tax_upto']}\n"
                if vdata.get('insurance_company'):
                    ins = vdata['insurance_company'][:30]
                    formatted += f"🛡️ **Insurance:** {ins}\n"
                if vdata.get('insurance_upto'):
                    formatted += f"📅 **Valid:** {vdata['insurance_upto']}\n"
        
        else:
            # Fallback for other API formats
            for key, value in data.items():
                if key in ['seller', 'success', 'status'] or key.startswith('@'):
                    continue
                
                key_formatted = key.replace('_', ' ').title()
                
                if isinstance(value, dict):
                    formatted += f"\n**{key_formatted}:**\n"
                    for k, v in value.items():
                        if v and str(v).strip():
                            formatted += f"• {k}: {v}\n"
                elif isinstance(value, list):
                    formatted += f"\n**{key_formatted}:**\n"
                    for item in value[:10]:
                        formatted += f"• {item}\n"
                else:
                    if value and str(value).strip():
                        formatted += f"**{key_formatted}:** {value}\n"
        
        formatted += "\n```\n"
        formatted += "╔═══════════════════════════════╗\n"
        formatted += "║   🎯 by P1yu5h{6_9} 💀        ║\n"
        formatted += "╚═══════════════════════════════╝\n"
        formatted += "```"
        
        return formatted
        
    except Exception as e:
        return f"❌ **ERROR:** Unable to parse data\n```\n{str(e)}\n```"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    credits = get_credits(user_id)
    
    # Show credits only for non-admin users
    if username == ADMIN_USERNAME:
        credit_msg = ""
    else:
        credit_msg = f"💳 **Your Credits:** {credits}\n\n"
    
    msg = (
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║    💀 OSINT BOT ACTIVATED 💀  ║\n"
        "║      by P1yu5h{6_9}           ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        f"{credit_msg}"
        "```\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "```\n"
        "🔍 **OSINT RECONNAISSANCE**\n\n"
        "`/num` - Phone Number Intel\n"
        "`/vehicle` - Vehicle Registration\n"
        "`/gmail` - Email Investigation\n"
        "`/ip` - IP Address Tracking\n"
        "`/imei` - Device Information\n"
        "`/pincode` - Location Data\n"
        "`/ifsc` - Bank Details\n\n"
        "```\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "```\n"
        "💣 **OFFENSIVE OPERATIONS**\n\n"
        "`/bomber` - SMS Flood Attack\n"
        "`/generate` - AI Image Generator\n\n"
        "```\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "```\n"
        "🤖 **AI & LEARNING**\n\n"
        "`/ai` - AI Assistant (FREE)\n"
        "`/osint` - OSINT Resources\n"
        "`/bugbounty` - Bug Bounty Resources\n"
        "`/sqllearn` - SQL Training Game\n\n"
        "```\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "```\n"
        "⚔️ **CTF WARFARE**\n\n"
        "`/ctf` - Team Achievements\n"
        "`/blackhatcomrade` - CTF Arsenal\n\n"
        "```\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "```\n"
        "ℹ️ **SYSTEM INFO**\n\n"
        "`/about` - Bot Information\n"
        "`/credits` - Check Balance\n"
        "`/help` - Help Menu\n"
    )
    
    if username == ADMIN_USERNAME:
        msg += (
            "\n```\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "```\n"
            "🔐 **ADMIN PANEL**\n\n"
            "`/addcredit <id> <amount>` - Add Credits\n"
            "`/addfreegroup` - Grant Free Access\n"
            "`/removefreegroup` - Revoke Access\n\n"
            "```\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "```\n"
            "💀 **SPAM COMMANDS**\n\n"
            "`/spam <id> <count> <msg>` - Spam User\n"
            "`/groupspam <count> <msg>` - Spam Group\n"
            "`/stopspam` - Stop All Spam\n"
            "`/spamusers` - List Spam Users\n"
            "`/allowspam <id>` - Grant Spam Access\n"
            "`/revokespam <id>` - Revoke Spam Access\n\n"
            "```\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "```\n"
            "📊 **ADMIN DASHBOARD**\n\n"
            "`/stats` - Bot Statistics\n"
            "`/logs` - View Recent Logs\n"
            "`/block <id>` - Block User\n"
            "`/unblock <id>` - Unblock User\n"
            "`/blocked` - List Blocked Users\n\n"
            "```\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "```\n"
            "🔧 **API MANAGEMENT**\n\n"
            "`/listapis` - List All Features\n"
            "`/getapi <feature>` - View API URL\n"
            "`/setapi <feature> <url>` - Change API\n\n"
            "`/aiapis` - View AI APIs\n"
            "`/setai <api> <url>` - Change AI API\n\n"
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   💀 MASTER ACCESS ACTIVE 💀  ║\n"
            "╚═══════════════════════════════╝\n"
            "```"
        )
    else:
        msg += (
            "\n```\n"
            "╔═══════════════════════════════╗\n"
            "║  🎯 READY TO EXTRACT DATA 🎯  ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            f"💡 Each command = 1 credit\n"
            f"💰 Need more? @{ADMIN_USERNAME}"
        )
    
    await update.message.reply_text(msg, parse_mode='Markdown')


async def num_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    chat_id = update.effective_chat.id
    credits = get_credits(user_id)
    
    # Check if user is blocked
    if is_user_blocked(user_id):
        await update.message.reply_text(
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   🚫 ACCESS DENIED 🚫         ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            "❌ You are blocked from using this bot\n"
            f"💡 Contact @{ADMIN_USERNAME}",
            parse_mode='Markdown'
        )
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ **USAGE:** `/num 9999565653`", parse_mode='Markdown')
        return
    
    number = context.args[0]
    
    # Log command
    log_command(user_id, username, "/num", f"Number: {number}")
    
    # Check if number is restricted
    if number in RESTRICTED_NUMBERS:
        await update.message.reply_text(
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   ⚠️ ACCESS DENIED ⚠️         ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            "🚫 **DON'T TRY TO BE OVERSMART**\n"
            "**BY SEARCHING MASTER'S NUMBER**\n"
            "**YOU BITCH!** 💀\n\n"
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   🔒 RESTRICTED NUMBER 🔒     ║\n"
            "╚═══════════════════════════════╝\n"
            "```",
            parse_mode='Markdown'
        )
        return
    
    if not is_free_group(chat_id) and credits <= 0:
        await update.message.reply_text(
            f"❌ **INSUFFICIENT CREDITS**\n\n"
            f"💳 Your Credits: {credits}\n"
            f"💰 Contact @{ADMIN_USERNAME} to buy more!",
            parse_mode='Markdown'
        )
        return

    deduct_credit(user_id, chat_id)
    
    if is_free_group(chat_id):
        await update.message.reply_text(f"```\n⏳ SCANNING DATABASE...\n🆓 FREE GROUP MODE\n```", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"```\n⏳ SCANNING DATABASE...\n💳 Credits Left: {get_credits(user_id)}\n```", parse_mode='Markdown')
    
    try:
        url = API_URLS['num'] + number
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Referer': 'https://osint-num-info.gauravcyber0.workers.dev/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            response_data = r.text
            # Check if response has actual data
            if response_data and len(response_data) > 50:
                try:
                    # Parse and mask the response
                    data = json.loads(response_data)
                    
                    # Mask seller fields
                    if 'seller' in data:
                        data['seller'] = "*** **** ** :- @***********"
                    if 'data' in data and '@Gauravcyber_op' in data['data']:
                        data['data']['@****_****'] = data['data'].pop('@Gauravcyber_op')
                    
                    # Format as clean JSON
                    formatted = "```json\n" + json.dumps(data, indent=2, ensure_ascii=False) + "\n```"
                    await update.message.reply_text(formatted, parse_mode=None)
                except Exception as format_error:
                    # If formatting fails, show raw data
                    await update.message.reply_text(
                        f"```\n⚠️ Format Error\n```\n"
                        f"Error: {str(format_error)[:100]}\n"
                        f"Response length: {len(response_data)}",
                        parse_mode='Markdown'
                    )
            else:
                await update.message.reply_text(
                    "```\n"
                    "╔═══════════════════════════════╗\n"
                    "║   🔧 UNDER MAINTENANCE 🔧    ║\n"
                    "╚═══════════════════════════════╝\n"
                    "```\n"
                    f"📱 Number: {number}\n"
                    "⚠️ Service is under maintenance\n\n"
                    "🔄 Please try again later\n"
                    f"💰 Credit refunded: +1",
                    parse_mode='Markdown'
                )
                add_credits(user_id, 1)
        else:
            await update.message.reply_text(
                "```\n"
                "╔═══════════════════════════════╗\n"
                "║   🔧 UNDER MAINTENANCE 🔧    ║\n"
                "╚═══════════════════════════════╝\n"
                "```\n"
                f"📱 Number: {number}\n"
                "⚠️ Service is under maintenance\n\n"
                "🔄 Please try again later\n"
                f"💰 Credit refunded: +1",
                parse_mode='Markdown'
            )
            add_credits(user_id, 1)
    except Exception as e:
        await update.message.reply_text(
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   🔧 UNDER MAINTENANCE 🔧    ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            "⚠️ Service is under maintenance\n"
            "🔄 Please try again later\n\n"
            f"💰 Credit refunded: +1",
            parse_mode='Markdown'
        )
        # Refund credit on error
        add_credits(user_id, 1)


async def vehicle_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    credits = get_credits(user_id)
    
    if not context.args:
        await update.message.reply_text("⚠️ **USAGE:** `/vehicle UP24AT0108`", parse_mode='Markdown')
        return
    
    if not is_free_group(chat_id) and credits <= 0:
        await update.message.reply_text(
            f"❌ **INSUFFICIENT CREDITS**\n\n"
            f"💳 Your Credits: {credits}\n"
            f"💰 Contact @{ADMIN_USERNAME} to buy more!",
            parse_mode='Markdown'
        )
        return

    deduct_credit(user_id, chat_id)
    vehicle = context.args[0]
    
    if is_free_group(chat_id):
        await update.message.reply_text(f"```\n⏳ SCANNING DATABASE...\n🆓 FREE GROUP MODE\n```", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"```\n⏳ SCANNING DATABASE...\n💳 Credits Left: {get_credits(user_id)}\n```", parse_mode='Markdown')
    
    url = API_URLS['vehicle'] + vehicle
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        }
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            formatted = format_json_response(r.text)
            await update.message.reply_text(formatted, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                "```\n❌ DATA NOT FOUND ❌\n```\n"
                f"🚗 Vehicle: {vehicle}\n"
                "⚠️ No data available",
                parse_mode='Markdown'
            )
    except Exception as e:
        await update.message.reply_text(
            "```\n⚠️ SERVICE ERROR ⚠️\n```\n"
            "❌ API unavailable\n"
            "💰 Credit refunded: +1",
            parse_mode='Markdown'
        )
        add_credits(user_id, 1)


async def pincode_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ USAGE: /pincode 400708")
        return

    pin = context.args[0]
    await update.message.reply_text("⏳ SCANNING DATABASE...")
    
    try:
        url = API_URLS['pincode'] + pin
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        }
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            # Parse and mask
            data = r.json()
            if isinstance(data, list):
                for item in data:
                    if 'api_sell' in item:
                        item['api_sell'] = "*** **** ** :- @***********"
            
            # Format as JSON
            formatted = "```json\n" + json.dumps(data, indent=2, ensure_ascii=False) + "\n```"
            await update.message.reply_text(formatted)
        else:
            await update.message.reply_text("❌ DATA NOT FOUND")
    except Exception as e:
        await update.message.reply_text(f"⚠️ ERROR: {str(e)[:100]}")


async def ifsc_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ **USAGE:** `/ifsc UBIN0548430`", parse_mode='Markdown')
        return

    ifsc = context.args[0]
    await update.message.reply_text("```\n⏳ SCANNING DATABASE...\n```", parse_mode='Markdown')
    url = API_URLS['ifsc'] + ifsc
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }
    r = requests.get(url, headers=headers, timeout=15).text
    formatted = format_json_response(r)
    await update.message.reply_text(formatted, parse_mode='Markdown')


async def ip_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ **USAGE:** `/ip 8.8.8.8`", parse_mode='Markdown')
        return

    ip = context.args[0]
    await update.message.reply_text("```\n⏳ TRACING IP...\n```", parse_mode='Markdown')
    url = f"http://ip-api.com/json/{ip}"
    try:
        r = requests.get(url).json()
        formatted = (
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║     🌐 IP TRACED 🌐           ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            f"💎 **IP ADDRESS**\n```\n└─► {r.get('query', 'N/A')}\n```\n"
            f"💎 **COUNTRY**\n```\n└─► {r.get('country', 'N/A')}\n```\n"
            f"💎 **REGION**\n```\n└─► {r.get('regionName', 'N/A')}\n```\n"
            f"💎 **CITY**\n```\n└─► {r.get('city', 'N/A')}\n```\n"
            f"💎 **ISP**\n```\n└─► {r.get('isp', 'N/A')}\n```\n"
            f"💎 **TIMEZONE**\n```\n└─► {r.get('timezone', 'N/A')}\n```\n"
            f"💎 **LAT/LON**\n```\n└─► {r.get('lat', 'N/A')}, {r.get('lon', 'N/A')}\n```\n"
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   🎯 Response by P1yu5h{6_9}  ║\n"
            "║      💀 OSINT MASTER 💀       ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💀 Stay Anonymous, Stay Safe 💀\n🔐 Hack The Planet! 🔐"
        )
        await update.message.reply_text(formatted, parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ **ERROR:** Unable to trace IP", parse_mode='Markdown')


async def gmail_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    credits = get_credits(user_id)
    
    if not context.args:
        await update.message.reply_text("⚠️ **USAGE:** `/gmail example@gmail.com`", parse_mode='Markdown')
        return
    
    if not is_free_group(chat_id) and credits <= 0:
        await update.message.reply_text(
            f"❌ **INSUFFICIENT CREDITS**\n\n"
            f"💳 Your Credits: {credits}\n"
            f"💰 Contact @{ADMIN_USERNAME} to buy more!",
            parse_mode='Markdown'
        )
        return

    deduct_credit(user_id, chat_id)
    email = context.args[0]
    
    if is_free_group(chat_id):
        await update.message.reply_text(f"```\n⏳ SCANNING EMAIL...\n🆓 FREE GROUP MODE\n```", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"```\n⏳ SCANNING EMAIL...\n💳 Credits Left: {get_credits(user_id)}\n```", parse_mode='Markdown')
    
    url = API_URLS['gmail'] + email
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        }
        r = requests.get(url, headers=headers, timeout=15).text
        formatted = format_json_response(r)
        await update.message.reply_text(formatted, parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ **ERROR:** Unable to fetch email info", parse_mode='Markdown')


async def imei_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ **USAGE:** `/imei 355333081034452`", parse_mode='Markdown')
        return

    imei = context.args[0]
    await update.message.reply_text("```\n⏳ SCANNING IMEI...\n```", parse_mode='Markdown')
    url = API_URLS['imei'] + imei
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        }
        r = requests.get(url, headers=headers, timeout=15).text
        formatted = format_json_response(r)
        await update.message.reply_text(formatted, parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ **ERROR:** Unable to fetch IMEI info", parse_mode='Markdown')


async def generate_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ **USAGE:** `/generate Electricity`", parse_mode='Markdown')
        return

    prompt = ' '.join(context.args)
    await update.message.reply_text("```\n⏳ GENERATING IMAGE...\n```", parse_mode='Markdown')
    url = f"https://song-generate-api.vercel.app/generate?prompt={prompt}"
    try:
        await update.message.reply_text(
            f"🎨 **IMAGE GENERATED**\n\n"
            f"🔗 [Click here to view]({url})\n\n"
            f"```\n"
            f"╔═══════════════════════════════╗\n"
            f"║   🎯 Response by P1yu5h{{6_9}}  ║\n"
            f"║      💀 OSINT MASTER 💀       ║\n"
            f"╚═══════════════════════════════╝\n"
            f"```\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💀 Stay Anonymous, Stay Safe 💀\n🔐 Hack The Planet! 🔐",
            parse_mode='Markdown'
        )
    except:
        await update.message.reply_text("❌ **ERROR:** Unable to generate image", parse_mode='Markdown')


async def add_free_group_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_user = update.effective_user.username
    
    if admin_user != ADMIN_USERNAME:
        await update.message.reply_text("❌ **UNAUTHORIZED:** Master only command!", parse_mode='Markdown')
        return
    
    chat_id = update.effective_chat.id
    
    if add_free_group(chat_id):
        await update.message.reply_text(
            f"```\n"
            f"╔═══════════════════════════════╗\n"
            f"║   ✅ GROUP ADDED ✅           ║\n"
            f"╚═══════════════════════════════╝\n"
            f"```\n"
            f"🆓 **This group is now FREE!**\n"
            f"📱 **Group ID:** {chat_id}\n"
            f"💀 All commands are free in this group\n\n"
            f"```\n"
            f"╔═══════════════════════════════╗\n"
            f"║   💀 MASTER COMMAND 💀        ║\n"
            f"╚═══════════════════════════════╝\n"
            f"```",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("⚠️ This group is already in free list!", parse_mode='Markdown')


async def remove_free_group_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_user = update.effective_user.username
    
    if admin_user != ADMIN_USERNAME:
        await update.message.reply_text("❌ **UNAUTHORIZED:** Master only command!", parse_mode='Markdown')
        return
    
    chat_id = update.effective_chat.id
    
    if remove_free_group(chat_id):
        await update.message.reply_text(
            f"```\n"
            f"╔═══════════════════════════════╗\n"
            f"║   ✅ GROUP REMOVED ✅         ║\n"
            f"╚═══════════════════════════════╝\n"
            f"```\n"
            f"💳 **Credits mode enabled**\n"
            f"📱 **Group ID:** {chat_id}\n"
            f"💰 Users need credits now\n\n"
            f"```\n"
            f"╔═══════════════════════════════╗\n"
            f"║   💀 MASTER COMMAND 💀        ║\n"
            f"╚═══════════════════════════════╝\n"
            f"```",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("⚠️ This group is not in free list!", parse_mode='Markdown')


async def credits_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    credits = get_credits(user_id)
    msg = (
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║      💳 CREDITS STATUS 💳     ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        f"💰 **Your Credits:** {credits}\n\n"
        f"💡 Each command uses 1 credit\n"
        f"🔥 Want more credits?\n"
        f"📞 Contact @{ADMIN_USERNAME}\n\n"
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║   🎯 by P1yu5h{6_9} 💀        ║\n"
        "╚═══════════════════════════════╝\n"
        "```"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')


async def add_credit_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_user = update.effective_user.username
    
    if admin_user != ADMIN_USERNAME:
        await update.message.reply_text("❌ **UNAUTHORIZED:** Master only command!", parse_mode='Markdown')
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ **USAGE:** `/addcredit <user_id> <amount>`\n\n"
            "Example: `/addcredit 123456789 50`\n\n"
            "💀 **Master Command Only**",
            parse_mode='Markdown'
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        amount = int(context.args[1])
        add_credits(target_user_id, amount)
        await update.message.reply_text(
            f"```\n"
            f"╔═══════════════════════════════╗\n"
            f"║   ✅ CREDITS ADDED ✅         ║\n"
            f"╚═══════════════════════════════╝\n"
            f"```\n"
            f"👤 **User ID:** {target_user_id}\n"
            f"💰 **Added:** {amount} credits\n"
            f"💳 **New Balance:** {get_credits(target_user_id)} credits\n\n"
            f"```\n"
            f"╔═══════════════════════════════╗\n"
            f"║   💀 MASTER COMMAND 💀        ║\n"
            f"╚═══════════════════════════════╝\n"
            f"```",
            parse_mode='Markdown'
        )
    except:
        await update.message.reply_text("❌ **ERROR:** Invalid user ID or amount", parse_mode='Markdown')


async def bomber(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    credits = get_credits(user_id)
    
    if not context.args:
        await update.message.reply_text("⚠️ **USAGE:** `/bomber 9999999999`\n\n💡 **To stop:** `/bomber stop`", parse_mode='Markdown')
        return
    
    # Check if user wants to stop
    if context.args[0].lower() == 'stop':
        await update.message.reply_text(
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   🛑 BOMBER STOPPED 🛑        ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            "🛑 Bomber operation terminated!",
            parse_mode='Markdown'
        )
        return
    
    phone = context.args[0]
    
    # Check if number is restricted
    if phone in RESTRICTED_NUMBERS:
        await update.message.reply_text(
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   ⚠️ ACCESS DENIED ⚠️         ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            "🚫 **DON'T TRY TO BE OVERSMART**\n"
            "**BITCH!** 💀\n\n"
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   🔒 RESTRICTED NUMBER 🔒     ║\n"
            "╚═══════════════════════════════╝\n"
            "```",
            parse_mode='Markdown'
        )
        return
    
    if not is_free_group(chat_id) and credits <= 0:
        await update.message.reply_text(
            f"❌ **INSUFFICIENT CREDITS**\n\n"
            f"💳 Your Credits: {credits}\n"
            f"💰 Contact @{ADMIN_USERNAME} to buy more!",
            parse_mode='Markdown'
        )
        return

    deduct_credit(user_id, chat_id)
    
    if is_free_group(chat_id):
        await update.message.reply_text(f"```\n⏳ INITIATING BOMBER...\n🆓 FREE GROUP MODE\n```", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"```\n⏳ INITIATING BOMBER...\n💳 Credits Left: {get_credits(user_id)}\n```", parse_mode='Markdown')
    
    url = API_URLS['bomber'] + phone
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        }
        r = requests.get(url, headers=headers, timeout=15)
        
        if r.status_code == 200:
            response_text = r.text
            
            # Check if response has data
            if response_text and len(response_text) > 50:
                try:
                    # Parse bomber response
                    data = r.json()
                    
                    # Mask seller info
                    if 'developer' in data:
                        data['developer'] = '@****_****'
                    
                    # Format bomber response
                    formatted = (
                        "```\n"
                        "╔═══════════════════════════════╗\n"
                        "║   💣 BOMBER ACTIVATED 💣      ║\n"
                        "╚═══════════════════════════════╝\n"
                        "```\n"
                        f"📱 **Target:** {data.get('phone', phone)}\n"
                        f"⏱️ **Duration:** {data.get('duration', 'N/A')} seconds\n"
                        f"🎯 **Total APIs:** {data.get('total_apis', 0)}\n"
                        f"✅ **Success:** {data.get('success', 0)}\n"
                        f"❌ **Failed:** {data.get('failed', 0)}\n\n"
                        "```\n"
                        "╔═══════════════════════════════╗\n"
                        "║   🎯 by P1yu5h{6_9} 💀        ║\n"
                        "╚═══════════════════════════════╝\n"
                        "```"
                    )
                    await update.message.reply_text(formatted, parse_mode='Markdown')
                except:
                    # If JSON parsing fails, show raw response
                    await update.message.reply_text(
                        "```\n"
                        "╔═══════════════════════════════╗\n"
                        "║   💣 BOMBER ACTIVATED 💣      ║\n"
                        "╚═══════════════════════════════╝\n"
                        "```\n"
                        f"📱 Target: {phone}\n"
                        f"✅ Bomber initiated successfully!",
                        parse_mode='Markdown'
                    )
            else:
                await update.message.reply_text(
                    "```\n"
                    "╔═══════════════════════════════╗\n"
                    "║   🔧 UNDER MAINTENANCE 🔧    ║\n"
                    "╚═══════════════════════════════╝\n"
                    "```\n"
                    f"📱 Number: {phone}\n"
                    "⚠️ Service temporarily unavailable\n"
                    f"💰 Credit refunded: +1",
                    parse_mode='Markdown'
                )
                add_credits(user_id, 1)
        else:
            await update.message.reply_text(
                "```\n"
                "╔═══════════════════════════════╗\n"
                "║   🔧 UNDER MAINTENANCE 🔧    ║\n"
                "╚═══════════════════════════════╝\n"
                "```\n"
                f"📱 Number: {phone}\n"
                "⚠️ Service temporarily unavailable\n"
                f"💰 Credit refunded: +1",
                parse_mode='Markdown'
            )
            add_credits(user_id, 1)
    except Exception as e:
        await update.message.reply_text(
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   ⚠️ SERVICE ERROR ⚠️         ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            "❌ Unable to execute bomber\n"
            f"💰 Credit refunded: +1",
            parse_mode='Markdown'
        )
        add_credits(user_id, 1)


async def osint_resources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║   🔍 OSINT RESOURCES 🔍       ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        "🎯 **USEFUL OSINT TOOLS** 🎯\n\n"
        "🔹 [OSINT Framework](https://osintframework.com/)\n"
        "   └─► Complete OSINT tools collection\n\n"
        "🔹 [Osint.rocks](https://osint.rocks/)\n"
        "   └─► OSINT search engine\n\n"
        "🔹 [Yandex](https://yandex.com/)\n"
        "   └─► Russian search engine for OSINT\n\n"
        "🔹 [LocateFamily](https://locatefamily.com/)\n"
        "   └─► People search & tracking\n\n"
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║  🎯 by P1yu5h{6_9} 💀         ║\n"
        "╚═══════════════════════════════╝\n"
        "```"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║      💀 ABOUT THIS BOT 💀     ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        "🎯 *OSINT Intelligence Bot*\n\n"
        "👤 *Developer:* @Piyushhu\n"
        "⚡ *Coded by:* P1yu5h\\{6\\_9\\}\n"
        "🔐 *Version:* 1\\.0\n"
        "💀 *Status:* Fully Operational\n\n"
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║  🎯 PASSIONATE LEARNERS 🎯    ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        "🔥 *Do you do CTF or Bug Bounty?*\n"
        "💡 We are passionate for learning\n"
        "🚀 Join us in the journey of\n"
        "   cybersecurity and OSINT\\!\n\n"
        "📝 *Check out my CTF Writeup:*\n"
        "🏆 HackOrN CTF 2025 \\- 12th Place\n"
        "🔗 [Read on Medium](https://medium.com/@piyushdhariwal2004/hackor-n-ctf-2025-qualifiers-my-12th-place-walkthrough-d081cbcd1ef1)\n\n"
        "🎓 *Interested in CTF?*\n"
        "🔥 Practice on [PicoCTF](https://picoctf.org/)\n"
        "💪 Best platform for beginners\\!\n\n"
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║   💀 OSINT MASTER ACTIVE 💀   ║\n"
        "╚═══════════════════════════════╝\n"
        "```"
    )
    await update.message.reply_text(msg, parse_mode='MarkdownV2')


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    
    msg = (
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║       💀 HELP MENU 💀         ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        "⚡ **COMMAND USAGE** ⚡\n\n"
        "🔹 `/num 9999565653`\n   └─► Get phone number details\n\n"
        "🔹 `/vehicle UP24AT0108`\n   └─► Get vehicle registration info\n\n"
        "🔹 `/pincode 400708`\n   └─► Get pincode location details\n\n"
        "🔹 `/ifsc UBIN0548430`\n   └─► Get bank IFSC details\n\n"
        "🔹 `/ip 8.8.8.8`\n   └─► Trace IP geolocation\n\n"
        "🔹 `/gmail example@gmail.com`\n   └─► Get Gmail account info\n\n"
        "🔹 `/imei 355333081034452`\n   └─► Get IMEI device info\n\n"
        "🔹 `/generate Electricity`\n   └─► Generate AI image\n\n"
        "🔹 `/bomber 9999999999`\n   └─► SMS Bomber attack\n\n"
        "🔹 `/credits`\n   └─► Check your credit balance\n\n"
        "🔹 `/ctf`\n   └─► BLACKHAT COMRADE team info\n\n"
        "🔹 `/blackhatcomrade`\n   └─► Complete CTF categories guide\n\n"
        "🔹 `/bugbounty`\n   └─► Bug bounty resources & drive\n\n"
        "🔹 `/sqllearn`\n   └─► SQL learning game\n\n"
        "🔹 `/osint`\n   └─► Useful OSINT resources\n"
    )
    
    if username == ADMIN_USERNAME:
        msg += (
            "\n```\n"
            "╔═══════════════════════════════╗\n"
            "║   💀 MASTER COMMANDS 💀       ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            "🔹 `/addcredit <user_id> <amount>`\n"
            "   └─► Add credits to user\n\n"
            "🔹 `/addfreegroup`\n"
            "   └─► Make this group free (use in group)\n\n"
            "🔹 `/removefreegroup`\n"
            "   └─► Remove free access (use in group)\n\n"
            "🔹 `/block <user_id>` - Block user\n"
            "🔹 `/unblock <user_id>` - Unblock user\n"
            "🔹 `/stats` - Bot statistics\n"
            "🔹 `/logs` - View command logs\n"
            "🔹 `/blocked` - List blocked users\n\n"
            "🔹 `/allowspam <user_id>` - Allow spam access\n"
            "🔹 `/revokespam <user_id>` - Revoke spam access\n"
            "🔹 `/spamusers` - List spam users\n\n"
            "**🔧 API MANAGEMENT:**\n"
            "🔹 `/listapis` - List all features\n"
            "🔹 `/getapi <feature>` - View API URL\n"
            "🔹 `/setapi <feature> <url>` - Change API URL\n"
        )
    
    msg += (
        "\n```\n"
        "╔═══════════════════════════════╗\n"
        "║  🎯 by P1yu5h{6_9} 💀         ║\n"
        "╚═══════════════════════════════╝\n"
        "```"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')


async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ **USAGE:** `/ai What is OSINT?`", parse_mode='Markdown')
        return
    
    question = ' '.join(context.args)
    await update.message.reply_text("```\n🤖 P1yu5h{6_9} AI THINKING...\n```", parse_mode='Markdown')
    
    ai_response = None
    
    # Try multiple AI APIs
    try:
        import urllib.parse
        encoded_question = urllib.parse.quote(question)
        
        # API 1: Blackbox AI
        try:
            url = API_URLS['ai_blackbox'] + encoded_question
            response = requests.get(url, timeout=10)
            
            # Check if response is HTML (bot protection)
            if response.status_code == 200 and 'text/html' not in response.headers.get('content-type', ''):
                # Try JSON first
                try:
                    data = response.json()
                    # Try different possible response keys
                    if 'response' in data:
                        ai_response = data['response']
                    elif 'answer' in data:
                        ai_response = data['answer']
                    elif 'result' in data:
                        ai_response = data['result']
                    elif 'message' in data:
                        ai_response = data['message']
                    elif 'text' in data:
                        ai_response = data['text']
                except:
                    # If not JSON, use plain text response
                    text = response.text.strip()
                    # Check if it's not HTML
                    if not text.startswith('<') and len(text) > 10:
                        ai_response = text
        except:
            pass
        
        # API 2: Gemini
        if not ai_response:
            try:
                url = API_URLS['ai_gemini'] + encoded_question
                response = requests.get(url, timeout=10)
                if response.status_code == 200 and 'text/html' not in response.headers.get('content-type', ''):
                    try:
                        data = response.json()
                        if 'response' in data:
                            ai_response = data['response']
                        elif 'answer' in data:
                            ai_response = data['answer']
                    except:
                        text = response.text.strip()
                        if not text.startswith('<') and len(text) > 10:
                            ai_response = text
            except:
                pass
        
        # API 3: ChatGPT
        if not ai_response:
            try:
                url = API_URLS['ai_chatgpt'] + encoded_question
                response = requests.get(url, timeout=10)
                if response.status_code == 200 and 'text/html' not in response.headers.get('content-type', ''):
                    try:
                        data = response.json()
                        if 'response' in data:
                            ai_response = data['response']
                        elif 'answer' in data:
                            ai_response = data['answer']
                    except:
                        text = response.text.strip()
                        if not text.startswith('<') and len(text) > 10:
                            ai_response = text
            except:
                pass
        
        # If got response, format and send
        if ai_response:
            ai_response = ai_response.strip()
            if len(ai_response) > 800:
                ai_response = ai_response[:800] + "..."
            
            # Remove markdown that might break
            ai_response = ai_response.replace('*', '').replace('_', '').replace('`', '')
            
            formatted = (
                "```\n"
                "╔═══════════════════════════════╗\n"
                "║   🤖 P1yu5h{6_9} AI 🤖        ║\n"
                "╚═══════════════════════════════╝\n"
                "```\n"
                f"💬 Q: {question}\n\n"
                f"🤖 A: {ai_response}\n\n"
                "```\n"
                "╔═══════════════════════════════╗\n"
                "║   🎯 by P1yu5h{6_9} 💀        ║\n"
                "╚═══════════════════════════════╝\n"
                "```"
            )
            await update.message.reply_text(formatted, parse_mode='Markdown')
        else:
            raise Exception("No AI response")
            
    except Exception as e:
        # Fallback response
        await update.message.reply_text(
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   🤖 P1yu5h{6_9} AI 🤖        ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            f"💬 Q: {question}\n\n"
            "🤖 A: AI service temporarily unavailable.\n\n"
            "⚠️ Possible reasons:\n"
            "• Rate limit exceeded\n"
            "• API maintenance\n"
            "• Network issue\n\n"
            f"💡 Try again in a few minutes or contact @{ADMIN_USERNAME}\n\n"
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   🎯 by P1yu5h{6_9} 💀        ║\n"
            "╚═══════════════════════════════╝\n"
            "```",
            parse_mode='Markdown'
        )

async def blackhat_comrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg1 = (
        "```\n"
        "╔═══════════════════════════════════════╗\n"
        "║  💀 BLACKHAT COMRADE GUIDE 💀         ║\n"
        "╚═══════════════════════════════════════╝\n"
        "```\n"
        "🏴 ABOUT BLACKHAT COMRADE\n\n"
        "We are a CTF team passionate about cybersecurity,\n"
        "ethical hacking, and competitive problem-solving.\n\n"
        "👤 Leader: Piyushhu (P1yu5h69)\n"
        "🏆 Achievements: Multiple top 10 finishes\n"
        "🎯 Focus: Jeopardy-style CTF competitions\n\n"
        "```\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "```\n"
        "🎮 WHAT IS CTF?\n\n"
        "CTF (Capture The Flag) is a cybersecurity\n"
        "competition where you solve challenges to\n"
        "find hidden flags.\n\n"
        "🔥 Types:\n"
        "• Jeopardy - Individual challenges\n"
        "• Attack-Defense - Real-time hacking\n"
        "• King of the Hill - Control systems\n\n"
        "💡 Skills Needed:\n"
        "• Cryptography\n"
        "• Web Exploitation\n"
        "• Reverse Engineering\n"
        "• Binary Exploitation\n"
        "• Forensics\n"
        "• OSINT\n\n"
        "```\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "   CTF CATEGORY BREAKDOWN\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "```"
    )
    
    msg2 = (
        "```\n"
        "━━━━━ 🔐 CRYPTOGRAPHY 🔐 ━━━━━\n"
        "```\n"
        "💀 What is it?\n"
        "Breaking encrypted messages, RSA/AES attacks,\n"
        "hash cracking, cipher solving\n\n"
        "🛠 Tools:\n"
        "• CyberChef - Universal decoder\n"
        "• RsaCtfTool - RSA attacks\n"
        "• John the Ripper - Hash cracking\n"
        "• Hashcat - GPU hash cracking\n\n"
        "```\n"
        "━━━━━ 🖼 STEGANOGRAPHY 🖼 ━━━━━\n"
        "```\n"
        "💀 What is it?\n"
        "Hidden data in images/audio/video\n\n"
        "🛠 Tools:\n"
        "• Steghide - Hide/extract data\n"
        "• Stegsolve - Image analysis\n"
        "• Binwalk - File carving\n"
        "• ExifTool - Metadata viewer\n\n"
        "```\n"
        "━━━━━ 🌐 WEB EXPLOITATION 🌐 ━━━━━\n"
        "```\n"
        "💀 What is it?\n"
        "SQL Injection, XSS, CSRF, LFI/RFI\n\n"
        "🛠 Tools:\n"
        "• Burp Suite - Web proxy\n"
        "• SQLmap - SQL injection\n"
        "• Nikto - Web scanner\n"
        "• Gobuster - Directory bruteforce"
    )
    
    msg3 = (
        "```\n"
        "━━━━━ 🔍 FORENSICS 🔍 ━━━━━\n"
        "```\n"
        "💀 What is it?\n"
        "Memory dumps, disk investigation\n\n"
        "🛠 Tools:\n"
        "• Volatility - Memory forensics\n"
        "• Wireshark - Packet analyzer\n"
        "• Autopsy - Disk analysis\n\n"
        "```\n"
        "━━━━━ 🔓 REVERSE ENGINEERING 🔓 ━━━━━\n"
        "```\n"
        "💀 What is it?\n"
        "Binary analysis, decompiling\n\n"
        "🛠 Tools:\n"
        "• Ghidra - NSA decompiler\n"
        "• IDA Pro - Disassembler\n"
        "• GDB - GNU debugger\n\n"
        "```\n"
        "━━━━━ 🎯 PWNING 🎯 ━━━━━\n"
        "```\n"
        "💀 What is it?\n"
        "Buffer overflow, ROP exploits\n\n"
        "🛠 Tools:\n"
        "• Pwntools - Exploit framework\n"
        "• ROPgadget - ROP chain builder\n\n"
        "```\n"
        "━━━━━ 🕵 OSINT 🕵 ━━━━━\n"
        "```\n"
        "💀 What is it?\n"
        "Open-source intelligence\n\n"
        "🛠 Tools:\n"
        "• Sherlock - Username search\n"
        "• Maltego - Link analysis\n\n"
        "```\n"
        "━━━━━ 🔌 NETWORKING 🔌 ━━━━━\n"
        "```\n"
        "💀 What is it?\n"
        "Network protocol analysis\n\n"
        "🛠 Tools:\n"
        "• Nmap - Port scanner\n"
        "• Netcat - Network swiss army\n"
        "• Aircrack-ng - WiFi cracking\n\n"
        "```\n"
        "╔═══════════════════════════════════════╗\n"
        "║   💀 BLACKHAT COMRADE 💀              ║\n"
        "║   🎯 by P1yu5h69 🎯                   ║\n"
        "╚═══════════════════════════════════════╝\n"
        "```\n"
        "🔥 We Do CTF Competitions! 💀"
    )
    
    await update.message.reply_text(msg1, parse_mode='Markdown')
    await update.message.reply_text(msg2, parse_mode='Markdown')
    await update.message.reply_text(msg3, parse_mode='Markdown')


async def bugbounty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg1 = (
        "╔═══════════════════════════════════════╗\n"
        "║    💰 BUG BOUNTY RESOURCES 💰         ║\n"
        "╚═══════════════════════════════════════╝\n\n"
        "🎯 What is Bug Bounty?\n\n"
        "Bug bounty programs reward security researchers\n"
        "for finding and reporting vulnerabilities.\n\n"
        "💰 Earn Money by Finding Bugs!\n"
        "Companies pay $100 to $100,000+ for valid bugs\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📚 COMPLETE BUG BOUNTY COLLECTION\n\n"
        "🔗 Google Drive Resources:\n"
        "https://drive.google.com/drive/folders/1pwlI8ewl5s8p-7IQ5oP2roAzUmJn_cWn\n\n"
        "📂 What's Inside:\n"
        "• Bug Bounty Methodologies\n"
        "• Vulnerability Reports\n"
        "• Tools and Scripts\n"
        "• Cheat Sheets\n"
        "• Video Tutorials\n"
        "• Practice Labs"
    )
    
    msg2 = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 TOP PLATFORMS:\n"
        "• HackerOne\n"
        "• Bugcrowd\n"
        "• Synack\n"
        "• Intigriti\n"
        "• YesWeHack\n\n"
        "🔥 COMMON VULNERABILITIES:\n"
        "• XSS\n"
        "• SQL Injection\n"
        "• IDOR\n"
        "• CSRF\n"
        "• Authentication Bypass\n"
        "• RCE\n\n"
        "╔═══════════════════════════════════════╗\n"
        "║   💀 BLACKHAT COMRADE 💀              ║\n"
        "║   🎯 by P1yu5h69 🎯                   ║\n"
        "╚═══════════════════════════════════════╝\n\n"
        "💰 Happy Hunting! �"
    )
    
    await update.message.reply_text(msg1)
    await update.message.reply_text(msg2)


async def sqllearn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "```\n"
        "╔═══════════════════════════════════════╗\n"
        "║      🎮 SQL LEARNING GAME 🎮          ║\n"
        "╚═══════════════════════════════════════╝\n"
        "```\n"
        "🎯 SQLPD - SQL Police Department\n\n"
        "Learn SQL through an interactive detective game!\n"
        "Solve crimes using SQL queries.\n\n"
        "```\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "```\n"
        "🔗 Play Now:\n"
        "https://sqlpd.com/\n\n"
        "🎮 What You'll Learn:\n"
        "• SELECT statements\n"
        "• WHERE clauses\n"
        "• JOIN operations\n"
        "• GROUP BY\n"
        "• Subqueries\n"
        "• Advanced SQL\n\n"
        "```\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "```\n"
        "💡 Why Learn SQL?\n"
        "• SQL Injection attacks\n"
        "• Database pentesting\n"
        "• Data forensics\n"
        "• Backend development\n"
        "• CTF competitions\n\n"
        "🔥 Other Resources:\n"
        "• SQLZoo\n"
        "• W3Schools SQL\n"
        "• HackerRank SQL\n"
        "• LeetCode Database\n\n"
        "```\n"
        "╔═══════════════════════════════════════╗\n"
        "║   💀 BLACKHAT COMRADE 💀              ║\n"
        "║   🎯 by P1yu5h{6_9} 🎯                ║\n"
        "╚═══════════════════════════════════════╝\n"
        "```\n"
        "🔥 Master SQL, Master Hacking!"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')


async def ctf_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║    💀 BLACKHAT COMRADE 💀     ║\n"
        "║      CTF TEAM INFO            ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        "🎯 **Team:** BLACKHAT COMRADE\n"
        "👤 **Leader:** @Piyushhu\n"
        "🏆 **Specialty:** CTF Competitions\n\n"
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║   🔥 WE DO CTF COMPETITIONS 🔥║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        "💀 **What We Do:**\n"
        "├─ Ethical Hacking & Web Security\n"
        "├─ Cryptography & OSINT\n"
        "├─ Reverse Engineering & Networking\n"
        "├─ Real-world Cybersecurity Challenges\n\n"
        "🏅 **TOP ACHIEVEMENTS:**\n"
        "🥇 CyberTea CTF - 4th Position\n"
        "🥇 Cruxipher CTF - 4th Position\n"
        "🥈 Digital CyberHunt CTF - 9th/200 teams\n"
        "🥈 H7CTF - 10th/320+ teams\n"
        "🥈 HackOrN CTF - 12th/400+ participants\n"
        "🎯 EnigmaXplore 3.0 CTF (IIIT Nagpur)\n"
        "🎯 KPMG Hackathon CTF 2025\n"
        "🎯 KIET Group of Institutions CTF\n"
        "💀 Multiple online cybersecurity challenges\n\n"
        "📝 **Read Our Writeups:**\n"
        "🔗 https://medium.com/@piyushdhariwal2004/hackor-n-ctf-2025-qualifiers-my-12th-place-walkthrough-d081cbcd1ef1\n\n"
        "🎓 **Want to Learn CTF?**\n"
        "🔥 Practice: https://picoctf.org/\n"
        "💪 Compete: https://ctftime.org/\n\n"
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║   💀 BLACKHAT COMRADE 💀      ║\n"
        "║   🎯 by P1yu5h{6_9} 🎯        ║\n"
        "╚═══════════════════════════════╝\n"
        "```"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')


# ============================================
# SPAM BOT COMMANDS
# ============================================

async def spam_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Check if user is admin or allowed
    if username != ADMIN_USERNAME and user_id not in allowed_spam_users:
        await update.message.reply_text(
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   ❌ ACCESS DENIED ❌         ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            "🚫 You don't have spam permission\n"
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
            await update.message.reply_text("⚠️ Maximum 100 messages allowed!")
            return
        
        await update.message.reply_text(
            f"```\n⏳ INITIATING SPAM...\n```\n"
            f"🎯 Target: {target_user_id}\n"
            f"📊 Count: {count}\n"
            f"💬 Message: {message[:50]}...",
            parse_mode='Markdown'
        )
        
        # Create spam bot instance
        from telegram import Bot
        import asyncio
        
        # Use main bot instead of spam bot (no separate hosting needed)
        spam_bot = context.bot  # Use OSINT bot itself
        
        task_id = f"{user_id}_{target_user_id}"
        spam_tasks[task_id] = True
        
        success = 0
        failed = 0
        
        for i in range(count):
            if task_id not in spam_tasks:
                break
            
            try:
                await spam_bot.send_message(chat_id=target_user_id, text=message)
                success += 1
                await asyncio.sleep(0.5)
            except Exception as send_error:
                failed += 1
                # Log first error for debugging
                if failed == 1:
                    error_msg = str(send_error)[:50]
        
        if task_id in spam_tasks:
            del spam_tasks[task_id]
        
        result_msg = (
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   ✅ SPAM COMPLETED ✅        ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            f"✅ Sent: {success}\n"
            f"❌ Failed: {failed}\n\n"
        )
        
        if failed > 0:
            result_msg += (
                "💡 **Why messages failed:**\n"
                "• User may have blocked the bot\n"
                "• Invalid user ID\n"
                "• Rate limit reached"
            )
        
        await update.message.reply_text(result_msg, parse_mode='Markdown')
        
    except ValueError:
        await update.message.reply_text("❌ Invalid user_id or count!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def group_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    chat_id = update.effective_chat.id
    
    if username != ADMIN_USERNAME and user_id not in allowed_spam_users:
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
            await update.message.reply_text("⚠️ Maximum 50 messages for group spam!")
            return
        
        await update.message.reply_text(
            f"```\n⏳ INITIATING GROUP SPAM...\n```\n"
            f"📊 Count: {count}",
            parse_mode='Markdown'
        )
        
        # Create spam bot instance
        from telegram import Bot
        import asyncio
        
        # Use main bot for group spam
        spam_bot = context.bot
        
        task_id = f"group_{chat_id}"
        spam_tasks[task_id] = True
        
        success = 0
        
        for i in range(count):
            if task_id not in spam_tasks:
                break
            
            try:
                await spam_bot.send_message(chat_id=chat_id, text=message)
                success += 1
                await asyncio.sleep(1)
            except:
                break
        
        if task_id in spam_tasks:
            del spam_tasks[task_id]
        
        await update.message.reply_text(
            f"```\n✅ COMPLETED ✅\n```\n"
            f"✅ Sent: {success}",
            parse_mode='Markdown'
        )
        
    except ValueError:
        await update.message.reply_text("❌ Invalid count!")


async def stop_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if username != ADMIN_USERNAME and user_id not in allowed_spam_users:
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


async def spam_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    
    if username != ADMIN_USERNAME:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if not allowed_spam_users:
        await update.message.reply_text("📋 No spam users allowed yet!")
        return
    
    user_list = "\n".join([f"• {uid}" for uid in allowed_spam_users])
    await update.message.reply_text(
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║   👥 SPAM USERS 👥            ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        f"**Total:** {len(allowed_spam_users)}\n\n"
        f"{user_list}",
        parse_mode='Markdown'
    )


async def allow_spam_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    
    if username != ADMIN_USERNAME:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ **USAGE:** `/allowspam <user_id>`",
            parse_mode='Markdown'
        )
        return
    
    try:
        user_id = int(context.args[0])
        allowed_spam_users.add(user_id)
        
        await update.message.reply_text(
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   ✅ SPAM ACCESS GRANTED ✅   ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            f"👤 User: {user_id}",
            parse_mode='Markdown'
        )
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")


async def revoke_spam_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    
    if username != ADMIN_USERNAME:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ **USAGE:** `/revokespam <user_id>`",
            parse_mode='Markdown'
        )
        return
    
    try:
        user_id = int(context.args[0])
        if user_id in allowed_spam_users:
            allowed_spam_users.remove(user_id)
            await update.message.reply_text(
                "```\n"
                "╔═══════════════════════════════╗\n"
                "║   ✅ SPAM ACCESS REVOKED ✅   ║\n"
                "╚═══════════════════════════════╝\n"
                "```\n"
                f"👤 User: {user_id}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("⚠️ User not in spam list!")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")


async def block_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    
    if username != ADMIN_USERNAME:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ **USAGE:** `/block <user_id>`",
            parse_mode='Markdown'
        )
        return
    
    try:
        user_id = int(context.args[0])
        blocked_users.add(user_id)
        await update.message.reply_text(
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   🚫 USER BLOCKED 🚫          ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            f"👤 User: {user_id}\n"
            "❌ Blocked from using bot",
            parse_mode='Markdown'
        )
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")


async def unblock_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    
    if username != ADMIN_USERNAME:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ **USAGE:** `/unblock <user_id>`",
            parse_mode='Markdown'
        )
        return
    
    try:
        user_id = int(context.args[0])
        if user_id in blocked_users:
            blocked_users.remove(user_id)
            await update.message.reply_text(
                "```\n"
                "╔═══════════════════════════════╗\n"
                "║   ✅ USER UNBLOCKED ✅        ║\n"
                "╚═══════════════════════════════╝\n"
                "```\n"
                f"👤 User: {user_id}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("⚠️ User not blocked!")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")


async def bot_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        f"👥 **Total Users:** {len(bot_users)}\n"
        f"🚫 **Blocked Users:** {len(blocked_users)}\n"
        f"🔥 **Spam Users:** {len(allowed_spam_users)}\n"
        f"📝 **Total Logs:** {len(user_logs)}\n"
        f"⚡ **Active Spam Tasks:** {len(spam_tasks)}\n\n"
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║   💀 by P1yu5h{6_9} 💀        ║\n"
        "╚═══════════════════════════════╝\n"
        "```",
        parse_mode='Markdown'
    )


async def view_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    
    if username != ADMIN_USERNAME:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if not user_logs:
        await update.message.reply_text("📋 No logs yet!")
        return
    
    # Show last 10 logs
    recent_logs = user_logs[-10:]
    log_text = "```\n╔═══════════════════════════════╗\n║   📝 RECENT LOGS 📝           ║\n╚═══════════════════════════════╝\n```\n\n"
    
    for log in reversed(recent_logs):
        log_text += (
            f"👤 **User:** {log['username']} ({log['user_id']})\n"
            f"⚡ **Command:** {log['command']}\n"
            f"📄 **Details:** {log['details'][:30]}...\n"
            f"🕐 **Time:** {log['timestamp']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )
    
    await update.message.reply_text(log_text, parse_mode='Markdown')


async def list_blocked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    
    if username != ADMIN_USERNAME:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if not blocked_users:
        await update.message.reply_text("📋 No blocked users!")
        return
    
    user_list = "\n".join([f"• {uid}" for uid in blocked_users])
    await update.message.reply_text(
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║   🚫 BLOCKED USERS 🚫         ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        f"**Total:** {len(blocked_users)}\n\n"
        f"{user_list}",
        parse_mode='Markdown'
    )


async def set_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to change API URL for a feature"""
    user = update.effective_user.username
    
    if user != ADMIN_USERNAME:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║      🔧 SET API URL 🔧       ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            "Usage: /setapi <feature> <url>\n\n"
            "Available Features:\n"
            "• num, vehicle, pincode\n"
            "• ifsc, ip, gmail, imei\n"
            "• bomber, ai_blackbox\n"
            "• ai_gemini, ai_chatgpt\n\n"
            "Example:\n"
            "/setapi num https://newapi.com/api/num?number="
        )
        return
    
    feature = context.args[0].lower()
    new_url = context.args[1]
    
    if feature not in API_URLS:
        await update.message.reply_text(
            f"❌ Invalid feature: {feature}\n\n"
            f"Available: {', '.join(API_URLS.keys())}"
        )
        return
    
    old_url = API_URLS[feature]
    API_URLS[feature] = new_url
    
    await update.message.reply_text(
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║    ✅ API URL UPDATED ✅     ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        f"Feature: {feature}\n\n"
        f"Old URL:\n{old_url}\n\n"
        f"New URL:\n{new_url}"
    )


async def get_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to view current API URL for a feature"""
    user = update.effective_user.username
    
    if user != ADMIN_USERNAME:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if len(context.args) < 1:
        # Show all APIs (excluding AI APIs)
        api_list = ""
        for feature, url in API_URLS.items():
            if not feature.startswith('ai_'):
                api_list += f"{feature}:\n{url}\n\n"
        
        await update.message.reply_text(
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║     📋 CURRENT API URLS 📋   ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n" + api_list
        )
        return
    
    feature = context.args[0].lower()
    
    if feature not in API_URLS:
        await update.message.reply_text(
            f"❌ Invalid feature: {feature}\n\n"
            f"Available: {', '.join([k for k in API_URLS.keys() if not k.startswith('ai_')])}"
        )
        return
    
    await update.message.reply_text(
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║      📋 API URL INFO 📋      ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        f"Feature: {feature}\n\n"
        f"URL:\n{API_URLS[feature]}"
    )


async def list_apis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to list all available API features"""
    user = update.effective_user.username
    
    if user != ADMIN_USERNAME:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    api_list = ""
    idx = 1
    for feature in API_URLS.keys():
        if not feature.startswith('ai_'):
            api_list += f"{idx}. {feature}\n"
            idx += 1
    
    await update.message.reply_text(
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║   📋 AVAILABLE FEATURES 📋   ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n" + api_list + "\n"
        "Commands:\n"
        "• /getapi <feature> - View API URL\n"
        "• /setapi <feature> <url> - Change API URL\n"
        "• /listapis - List all features\n\n"
        "For AI APIs use: /aiapis"
    )


async def get_ai_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to view AI API URLs"""
    user = update.effective_user.username
    
    if user != ADMIN_USERNAME:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    ai_list = ""
    for feature, url in API_URLS.items():
        if feature.startswith('ai_'):
            ai_list += f"{feature}:\n{url}\n\n"
    
    await update.message.reply_text(
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║      🤖 AI API URLS 🤖       ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n" + ai_list +
        "Commands:\n"
        "• /aiapis - View all AI APIs\n"
        "• /setai <api> <url> - Change AI API"
    )


async def set_ai_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to change AI API URL"""
    user = update.effective_user.username
    
    if user != ADMIN_USERNAME:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║      🤖 SET AI API 🤖        ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            "Usage: /setai <api> <url>\n\n"
            "Available AI APIs:\n"
            "• blackbox\n"
            "• gemini\n"
            "• chatgpt\n\n"
            "Example:\n"
            "/setai blackbox https://newai.com/chat?q="
        )
        return
    
    api_name = context.args[0].lower()
    new_url = context.args[1]
    
    # Map short names to full keys
    api_map = {
        'blackbox': 'ai_blackbox',
        'gemini': 'ai_gemini',
        'chatgpt': 'ai_chatgpt'
    }
    
    if api_name not in api_map:
        await update.message.reply_text(
            f"❌ Invalid AI API: {api_name}\n\n"
            f"Available: blackbox, gemini, chatgpt"
        )
        return
    
    feature = api_map[api_name]
    old_url = API_URLS[feature]
    API_URLS[feature] = new_url
    
    await update.message.reply_text(
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║   ✅ AI API UPDATED ✅       ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        f"AI API: {api_name}\n\n"
        f"Old URL:\n{old_url}\n\n"
        f"New URL:\n{new_url}"
    )


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("num", num_info))
app.add_handler(CommandHandler("vehicle", vehicle_info))
app.add_handler(CommandHandler("pincode", pincode_info))
app.add_handler(CommandHandler("ifsc", ifsc_info))
app.add_handler(CommandHandler("ip", ip_info))
app.add_handler(CommandHandler("gmail", gmail_info))
app.add_handler(CommandHandler("imei", imei_info))
app.add_handler(CommandHandler("generate", generate_photo))
app.add_handler(CommandHandler("bomber", bomber))
app.add_handler(CommandHandler("credits", credits_check))
app.add_handler(CommandHandler("osint", osint_resources))
app.add_handler(CommandHandler("addcredit", add_credit_cmd))
app.add_handler(CommandHandler("addfreegroup", add_free_group_cmd))
app.add_handler(CommandHandler("removefreegroup", remove_free_group_cmd))
app.add_handler(CommandHandler("about", about))
app.add_handler(CommandHandler("ctf", ctf_info))
app.add_handler(CommandHandler("bugbounty", bugbounty))
app.add_handler(CommandHandler("sqllearn", sqllearn))
app.add_handler(CommandHandler("blackhatcomrade", blackhat_comrade))
app.add_handler(CommandHandler("ai", ai_chat))
app.add_handler(CommandHandler("help", help_cmd))

# Spam commands
app.add_handler(CommandHandler("spam", spam_user))
app.add_handler(CommandHandler("groupspam", group_spam))
app.add_handler(CommandHandler("stopspam", stop_spam))
app.add_handler(CommandHandler("spamusers", spam_users_list))
app.add_handler(CommandHandler("allowspam", allow_spam_user))
app.add_handler(CommandHandler("revokespam", revoke_spam_user))

# Admin dashboard commands
app.add_handler(CommandHandler("block", block_user))
app.add_handler(CommandHandler("unblock", unblock_user))
app.add_handler(CommandHandler("stats", bot_stats))
app.add_handler(CommandHandler("logs", view_logs))
app.add_handler(CommandHandler("blocked", list_blocked))

# API management commands (admin only)
app.add_handler(CommandHandler("setapi", set_api))
app.add_handler(CommandHandler("getapi", get_api))
app.add_handler(CommandHandler("listapis", list_apis))

# AI API management commands (admin only)
app.add_handler(CommandHandler("aiapis", get_ai_api))
app.add_handler(CommandHandler("setai", set_ai_api))

# Start HTTP server in background
Thread(target=run_server, daemon=True).start()

print("Bot running...")
app.run_polling(drop_pending_updates=True)
