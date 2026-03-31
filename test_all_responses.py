#!/usr/bin/env python3
import requests
import json

def format_json_response(data):
    """Format JSON response - same as bot"""
    try:
        if isinstance(data, str):
            data = json.loads(data)
        
        # Mask seller value completely
        if 'seller' in data:
            data['seller'] = "*** **** ** :- @***********"
        
        # Mask @Gauravcyber_op to @****_****
        if 'data' in data and isinstance(data['data'], dict):
            if '@Gauravcyber_op' in data['data']:
                data['data']['@****_****'] = data['data'].pop('@Gauravcyber_op')
        
        return data
        
    except Exception as e:
        return f"ERROR: {str(e)}"


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive'
}

print("\n" + "="*70)
print("🔍 TESTING /num COMMAND")
print("="*70)

# Test 1: Phone Number
number = '9359910974'
url = f'https://osint-num-info.gauravcyber0.workers.dev/?mobile={number}'

try:
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code == 200:
        masked_data = format_json_response(r.json())
        print(f"\n✅ /num {number}")
        print("-"*70)
        print(json.dumps(masked_data, indent=2))
    else:
        print(f'❌ Status: {r.status_code}')
except Exception as e:
    print(f'❌ ERROR: {str(e)}')


print("\n\n" + "="*70)
print("🚗 TESTING /vehicle COMMAND")
print("="*70)

# Test 2: Vehicle
vehicle = 'DL01AB1234'
url = f'https://prosnal-vehicle.gauravcyber0.workers.dev/?vehicle={vehicle}'

try:
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code == 200:
        masked_data = format_json_response(r.json())
        print(f"\n✅ /vehicle {vehicle}")
        print("-"*70)
        print(json.dumps(masked_data, indent=2))
    else:
        print(f'❌ Status: {r.status_code}')
        print(f'Response: {r.text[:200]}')
except Exception as e:
    print(f'❌ ERROR: {str(e)}')


print("\n\n" + "="*70)
print("📍 TESTING /pincode COMMAND")
print("="*70)

# Test 3: Pincode
pincode = '400708'
url = f'https://pin-code-info.gauravcyber0.workers.dev/?pincode={pincode}'

try:
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code == 200:
        masked_data = format_json_response(r.json())
        print(f"\n✅ /pincode {pincode}")
        print("-"*70)
        print(json.dumps(masked_data, indent=2))
    else:
        print(f'❌ Status: {r.status_code}')
except Exception as e:
    print(f'❌ ERROR: {str(e)}')


print("\n" + "="*70)
print("✅ ALL TESTS COMPLETE")
print("="*70)
print("\n📋 MASKING APPLIED:")
print("  • seller: '*** **** ** :- @***********'")
print("  • @Gauravcyber_op → @****_****")
print("="*70 + "\n")
