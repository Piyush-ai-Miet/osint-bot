#!/usr/bin/env python3
import requests
import json

def format_json_response(data):
    """Format JSON response - same as bot"""
    try:
        if isinstance(data, str):
            data = json.loads(data)
        
        # Mask seller value only
        if 'seller' in data:
            data['seller'] = "API SELL BY :- @***********"
        
        # Mask @Gauravcyber_op to @****_****
        if 'data' in data and isinstance(data['data'], dict):
            if '@Gauravcyber_op' in data['data']:
                data['data']['@****_****'] = data['data'].pop('@Gauravcyber_op')
        
        return data
        
    except Exception as e:
        return f"ERROR: {str(e)}"


# Test with real API
number = '9359910974'
url = f'https://osint-num-info.gauravcyber0.workers.dev/?mobile={number}'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive'
}

print("="*60)
print(f"Testing /num {number}")
print("="*60)

try:
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code == 200:
        original_data = r.json()
        
        print("\n📥 ORIGINAL API RESPONSE:")
        print("-"*60)
        print(json.dumps(original_data, indent=2)[:500] + "...")
        
        # Apply masking
        masked_data = format_json_response(original_data)
        
        print("\n\n✅ MASKED RESPONSE (What bot will show):")
        print("="*60)
        print(json.dumps(masked_data, indent=2))
        
        print("\n\n📋 KEY CHANGES:")
        print("-"*60)
        print("✅ seller: 'API SELL BY :- @Gaurav_Cyber_Op' → 'API SELL BY :- @***********'")
        print("✅ @Gauravcyber_op → @****_****")
        print("✅ All other data remains intact")
        
    else:
        print(f'Status: {r.status_code}')
        
except Exception as e:
    print(f'ERROR: {str(e)}')
