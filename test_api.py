import requests
import json

# Browser headers to bypass bot detection
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://osint-num-info.gauravcyber0.workers.dev/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin'
}

def test_num_api(number):
    """Test phone number API"""
    print(f"\n{'='*50}")
    print(f"🔍 Testing /num API with: {number}")
    print(f"{'='*50}")
    
    url = f"https://osint-num-info.gauravcyber0.workers.dev/?mobile={number}"
    
    try:
        # Without headers
        print("\n❌ Testing WITHOUT headers...")
        r1 = requests.get(url, timeout=10)
        print(f"Status: {r1.status_code}")
        print(f"Response length: {len(r1.text)} chars")
        
        # With headers
        print("\n✅ Testing WITH headers...")
        r2 = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Status: {r2.status_code}")
        print(f"Response length: {len(r2.text)} chars")
        print(f"Content-Type: {r2.headers.get('content-type', 'N/A')}")
        
        if r2.status_code == 200:
            try:
                data = json.loads(r2.text)
                print(f"\n📊 Response Data:")
                print(json.dumps(data, indent=2)[:500])
            except:
                print(f"\n📊 Raw Response (first 300 chars):")
                print(r2.text[:300])
            print("\n✅ SUCCESS: API working with headers!")
        else:
            print(f"\n⚠️ WARNING: Got status {r2.status_code}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


def test_vehicle_api(vehicle):
    """Test vehicle API"""
    print(f"\n{'='*50}")
    print(f"🚗 Testing /vehicle API with: {vehicle}")
    print(f"{'='*50}")
    
    url = f"https://prosnal-vehicle.gauravcyber0.workers.dev/?vehicle={vehicle}"
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:200]}")
        
        if r.status_code == 200:
            print("✅ Vehicle API responding!")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


def test_gmail_api(email):
    """Test gmail API"""
    print(f"\n{'='*50}")
    print(f"📧 Testing /gmail API with: {email}")
    print(f"{'='*50}")
    
    url = f"https://gmail-info-api-two.vercel.app/info?mail={email}"
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Response length: {len(r.text)} chars")
        
        if r.status_code == 200:
            print("✅ Gmail API responding!")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("💀 OSINT BOT API TESTING 💀")
    print("="*50)
    
    # Test phone number API
    test_num_api("9999999999")
    
    # Test vehicle API
    test_vehicle_api("DL01AB1234")
    
    # Test gmail API
    test_gmail_api("test@gmail.com")
    
    print("\n" + "="*50)
    print("✅ Testing Complete!")
    print("="*50 + "\n")
