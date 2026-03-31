#!/usr/bin/env python3
"""
Test script to simulate what happens when someone tries to search restricted numbers
"""

# Restricted numbers (Master's numbers - DO NOT SEARCH)
RESTRICTED_NUMBERS = [
    "7505426304", 
    "8791199014"
]

def test_num_command(number):
    """Simulate /num command"""
    print(f"\n{'='*60}")
    print(f"Testing: /num {number}")
    print('='*60)
    
    # Check if number is restricted
    if number in RESTRICTED_NUMBERS:
        print("\n🚫 RESTRICTED NUMBER DETECTED!")
        print("\nBot will send this message:\n")
        print("```")
        print("╔═══════════════════════════════╗")
        print("║   ⚠️ ACCESS DENIED ⚠️         ║")
        print("╚═══════════════════════════════╝")
        print("```")
        print("🚫 **DON'T TRY TO BE OVERSMART**")
        print("**BY SEARCHING MASTER'S NUMBER**")
        print("**YOU BITCH!** 💀")
        print()
        print("```")
        print("╔═══════════════════════════════╗")
        print("║   🔒 RESTRICTED NUMBER 🔒     ║")
        print("╚═══════════════════════════════╝")
        print("```")
        print("\n❌ NO DATA WILL BE SHOWN")
        print("❌ NO CREDIT DEDUCTED")
        return False
    else:
        print("\n✅ NUMBER ALLOWED!")
        print("Bot will proceed to fetch data from API...")
        return True

def test_bomber_command(number):
    """Simulate /bomber command"""
    print(f"\n{'='*60}")
    print(f"Testing: /bomber {number}")
    print('='*60)
    
    # Check if number is restricted
    if number in RESTRICTED_NUMBERS:
        print("\n🚫 RESTRICTED NUMBER DETECTED!")
        print("\nBot will send this message:\n")
        print("```")
        print("╔═══════════════════════════════╗")
        print("║   ⚠️ ACCESS DENIED ⚠️         ║")
        print("╚═══════════════════════════════╝")
        print("```")
        print("🚫 **DON'T TRY TO BE OVERSMART**")
        print("**BITCH!** 💀")
        print()
        print("```")
        print("╔═══════════════════════════════╗")
        print("║   🔒 RESTRICTED NUMBER 🔒     ║")
        print("╚═══════════════════════════════╝")
        print("```")
        print("\n❌ BOMBER WILL NOT RUN")
        print("❌ NO CREDIT DEDUCTED")
        return False
    else:
        print("\n✅ NUMBER ALLOWED!")
        print("Bot will proceed to run bomber...")
        return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("💀 OSINT BOT RESTRICTION TEST 💀")
    print("="*60)
    
    # Test cases
    test_numbers = [
        "7505426304",   # Your number (RESTRICTED)
        "8791199014",   # Alt number (RESTRICTED)
        "9359910974",   # Previously restricted (NOW ALLOWED)
        "9999999999"    # Random number (ALLOWED)
    ]
    
    print("\n📱 TESTING /num COMMAND:")
    print("="*60)
    for num in test_numbers:
        test_num_command(num)
    
    print("\n\n💣 TESTING /bomber COMMAND:")
    print("="*60)
    for num in test_numbers:
        test_bomber_command(num)
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETE!")
    print("="*60)
    print("\n📋 SUMMARY:")
    print("  • 7505426304 - BLOCKED ❌")
    print("  • 8791199014 - BLOCKED ❌")
    print("  • 9359910974 - ALLOWED ✅")
    print("  • Other numbers - ALLOWED ✅")
    print("="*60 + "\n")
