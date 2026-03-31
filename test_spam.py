#!/usr/bin/env python3
"""
Test spam bot functionality
"""
import requests
import time

SPAM_BOT_TOKEN = "7866793934:AAGaIj4ZtGb1l_Ifud0miAoyyCHJMo3MQxw"

def get_bot_info():
    """Get spam bot info"""
    url = f"https://api.telegram.org/bot{SPAM_BOT_TOKEN}/getMe"
    r = requests.get(url)
    return r.json()

def send_test_message(user_id, message):
    """Send test message to user"""
    url = f"https://api.telegram.org/bot{SPAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": user_id,
        "text": message
    }
    r = requests.post(url, json=data)
    return r.json()

def spam_messages(user_id, count, message):
    """Spam multiple messages"""
    print(f"\n🔥 Starting spam to user {user_id}")
    print(f"📊 Count: {count}")
    print(f"💬 Message: {message}")
    print("="*60)
    
    success = 0
    failed = 0
    
    for i in range(count):
        try:
            result = send_test_message(user_id, f"{message} #{i+1}")
            if result.get('ok'):
                success += 1
                print(f"✅ Message {i+1}/{count} sent")
            else:
                failed += 1
                print(f"❌ Message {i+1}/{count} failed: {result.get('description')}")
            time.sleep(0.5)  # Delay to avoid rate limit
        except Exception as e:
            failed += 1
            print(f"❌ Message {i+1}/{count} error: {e}")
    
    print("\n" + "="*60)
    print(f"✅ Sent: {success}")
    print(f"❌ Failed: {failed}")
    print("="*60)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("💀 SPAM BOT TEST 💀")
    print("="*60)
    
    # Get bot info
    bot_info = get_bot_info()
    if bot_info.get('ok'):
        bot = bot_info['result']
        print(f"\n✅ Bot Connected!")
        print(f"Bot Name: {bot['first_name']}")
        print(f"Username: @{bot['username']}")
        print(f"Bot ID: {bot['id']}")
    else:
        print("❌ Bot connection failed!")
        exit(1)
    
    print("\n" + "="*60)
    print("📋 INSTRUCTIONS:")
    print("="*60)
    print("1. Open Telegram")
    print("2. Search for @Hackerhuu_bot")
    print("3. Click START")
    print("4. Get your user ID from @userinfobot")
    print("5. Enter your user ID below")
    print("="*60)
    
    # Get user input
    user_id = input("\n👤 Enter your Telegram User ID: ").strip()
    count = input("📊 How many messages? (1-10): ").strip()
    message = input("💬 Enter message: ").strip()
    
    try:
        user_id = int(user_id)
        count = int(count)
        
        if count > 10:
            print("⚠️ Max 10 messages for testing!")
            count = 10
        
        # Start spamming
        spam_messages(user_id, count, message)
        
    except ValueError:
        print("❌ Invalid input!")
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")
