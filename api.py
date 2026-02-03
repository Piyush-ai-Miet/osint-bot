import requests
import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Get token from environment variable (for security)
TOKEN = os.getenv("BOT_TOKEN", "8367270183:AAE1AlWPm1A3ILFulA-OnEFpVP_LkjDomp0")
ADMIN_USERNAME = "Piyushhu"
FREE_GROUPS = []  # List of group IDs where bot is free

# Credits storage (in production, use a database)
user_credits = {}


def is_free_group(chat_id):
    """Check if the chat is a free group"""
    return chat_id in FREE_GROUPS


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
    try:
        if isinstance(data, str):
            data = json.loads(data)
        
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
            
            # Process @Gauravcyber_op section (detailed records)
            if '@Gauravcyber_op' in api_data:
                gaurav_data = api_data['@Gauravcyber_op']
                if 'result' in gaurav_data and isinstance(gaurav_data['result'], list):
                    results = gaurav_data['result']
                    
                    # Remove duplicates based on mobile+name
                    seen = set()
                    unique_results = []
                    for item in results:
                        key = f"{item.get('mobile', '')}-{item.get('name', '')}"
                        if key not in seen:
                            seen.add(key)
                            unique_results.append(item)
                    
                    formatted += f"\n```\n━━━━━━━ 📋 RECORDS ({len(unique_results)}) ━━━━━━━\n```\n"
                    
                    formatted += f"\n```\n━━━━━━━ 📋 RECORDS ({len(unique_results)}) ━━━━━━━\n```\n"
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
                    
                    if len(unique_results) > 5:
                        formatted += f"_...and {len(unique_results) - 5} more records_\n"
            
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
        
        # PINCODE API - is a list with PostOffice key
        elif isinstance(data, list) and len(data) > 0 and 'PostOffice' in data[0]:
            pdata = data[0]
            if pdata.get('Message'):
                formatted += f"\n📊 **{pdata['Message']}**\n"
            
            if 'PostOffice' in pdata:
                for idx, po in enumerate(pdata['PostOffice'], 1):
                    formatted += f"\n```\n━━━━━━━ POST OFFICE #{idx} ━━━━━━━\n```\n"
                    
                    if po.get('Name'):
                        formatted += f"🏤 **Name:** {po['Name']}\n"
                    if po.get('BranchType'):
                        formatted += f"🏢 **Type:** {po['BranchType']}\n"
                    if po.get('DeliveryStatus'):
                        formatted += f"📦 **Delivery:** {po['DeliveryStatus']}\n"
                    if po.get('Block'):
                        formatted += f"📍 **Block:** {po['Block']}\n"
                    if po.get('District'):
                        formatted += f"🏙️ **District:** {po['District']}\n"
                    if po.get('State'):
                        formatted += f"🏛️ **State:** {po['State']}\n"
                    if po.get('Pincode'):
                        formatted += f"📮 **Pincode:** {po['Pincode']}\n"
        
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
    chat_id = update.effective_chat.id
    credits = get_credits(user_id)
    
    if not context.args:
        await update.message.reply_text("⚠️ **USAGE:** `/num 9999565653`", parse_mode='Markdown')
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
    number = context.args[0]
    
    if is_free_group(chat_id):
        await update.message.reply_text(f"```\n⏳ SCANNING DATABASE...\n🆓 FREE GROUP MODE\n```", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"```\n⏳ SCANNING DATABASE...\n💳 Credits Left: {get_credits(user_id)}\n```", parse_mode='Markdown')
    
    try:
        url = f"https://osint-num-info.gauravcyber0.workers.dev/?mobile={number}"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            formatted = format_json_response(r.text)
            await update.message.reply_text(formatted, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                "```\n"
                "╔═══════════════════════════════╗\n"
                "║   ❌ DATA NOT FOUND ❌        ║\n"
                "╚═══════════════════════════════╝\n"
                "```\n"
                f"📱 Number: {number}\n"
                "⚠️ No data available in database\n\n"
                "💡 Try another number or contact admin",
                parse_mode='Markdown'
            )
    except Exception as e:
        await update.message.reply_text(
            "```\n"
            "╔═══════════════════════════════╗\n"
            "║   ⚠️ SERVICE ERROR ⚠️         ║\n"
            "╚═══════════════════════════════╝\n"
            "```\n"
            "❌ API service temporarily unavailable\n"
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
    
    url = f"https://prosnal-vehicle.gauravcyber0.workers.dev/?vehicle={vehicle}"
    try:
        r = requests.get(url, timeout=15)
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
        await update.message.reply_text("⚠️ **USAGE:** `/pincode 400708`", parse_mode='Markdown')
        return

    pin = context.args[0]
    await update.message.reply_text("```\n⏳ SCANNING DATABASE...\n```", parse_mode='Markdown')
    
    try:
        url = f"https://pin-code-info.gauravcyber0.workers.dev/?pincode={pin}"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            formatted = format_json_response(r.text)
            await update.message.reply_text(formatted, parse_mode='Markdown')
        else:
            await update.message.reply_text("```\n❌ DATA NOT FOUND ❌\n```", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text("```\n⚠️ SERVICE ERROR ⚠️\n```", parse_mode='Markdown')


async def ifsc_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ **USAGE:** `/ifsc UBIN0548430`", parse_mode='Markdown')
        return

    ifsc = context.args[0]
    await update.message.reply_text("```\n⏳ SCANNING DATABASE...\n```", parse_mode='Markdown')
    url = f"https://ifsc-code-info.gauravcyber0.workers.dev/?ifsc={ifsc}"
    r = requests.get(url).text
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
    
    url = f"https://gmail-info-api-two.vercel.app/info?mail={email}"
    try:
        r = requests.get(url).text
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
    url = f"https://imei-number-infoo.vercel.app/api/imei?imei={imei}"
    try:
        r = requests.get(url).text
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
            "� Bomber operation terminated!",
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
    phone = context.args[0]
    
    if is_free_group(chat_id):
        await update.message.reply_text(f"```\n⏳ INITIATING BOMBER...\n🆓 FREE GROUP MODE\n```", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"```\n⏳ INITIATING BOMBER...\n💳 Credits Left: {get_credits(user_id)}\n```", parse_mode='Markdown')
    
    url = f"https://bomm.gauravcyber0.workers.dev/?phone={phone}"
    try:
        r = requests.get(url).text
        formatted = format_json_response(r)
        await update.message.reply_text(formatted, parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ **ERROR:** Unable to execute bomber", parse_mode='Markdown')


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
            "   └─► Remove free access (use in group)\n"
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
            url = f"https://api.blackbox.ai/api/chat?q={encoded_question}"
            response = requests.get(url, timeout=10)
            data = response.json()
            if 'response' in data:
                ai_response = data['response']
        except:
            pass
        
        # API 2: Gemini
        if not ai_response:
            try:
                url = f"https://api.ryzendesu.vip/api/ai/gemini?text={encoded_question}"
                response = requests.get(url, timeout=10)
                data = response.json()
                if 'response' in data:
                    ai_response = data['response']
            except:
                pass
        
        # API 3: ChatGPT
        if not ai_response:
            try:
                url = f"https://api.ryzendesu.vip/api/ai/chatgpt?text={encoded_question}"
                response = requests.get(url, timeout=10)
                data = response.json()
                if 'response' in data:
                    ai_response = data['response']
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
            "🤖 A: AI service temporarily unavailable. Try again later!\n\n"
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

print("Bot running...")
app.run_polling()
