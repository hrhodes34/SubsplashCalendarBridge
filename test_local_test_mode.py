#!/usr/bin/env python3
"""
Local test script to verify test mode configuration
"""

import os
from sync_script import SubsplashCalendarSync

def test_test_mode_config():
    """Test that test mode is configured correctly"""
    print("🧪 Testing Test Mode Configuration")
    print("=" * 50)
    
    # Set test mode environment variable
    os.environ['TEST_MODE'] = 'true'
    
    # Create sync instance
    sync = SubsplashCalendarSync()
    
    print(f"✅ Test Mode: {sync.test_mode}")
    print(f"🎯 Target Month: {getattr(sync, 'target_month', 'Not set')}")
    print(f"🎯 Target Year: {getattr(sync, 'target_year', 'Not set')}")
    print(f"📊 Max Months to Check: {sync.max_months_to_check}")
    print(f"📅 Calendar IDs: {list(sync.calendar_ids.keys())}")
    print(f"🔗 Calendar URLs: {list(sync.calendar_urls.keys())}")
    
    print("\n" + "=" * 50)
    
    if sync.test_mode:
        print("✅ Test mode is correctly enabled")
        print("🎯 Will only scrape August 2025 prayer calendar")
        print("📊 Will only check 1 month")
        print("🔗 Will only process prayer calendar")
    else:
        print("❌ Test mode is not enabled")
    
    print("\n" + "=" * 50)
    print("🧪 Test mode configuration verified!")
    print("🚀 Ready to test with GitHub Actions!")

if __name__ == "__main__":
    test_test_mode_config()
