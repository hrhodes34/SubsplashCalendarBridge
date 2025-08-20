#!/usr/bin/env python3
"""
Test script to verify that the browser navigation method in sync_script.py works correctly.
This will test the _scrape_calendar_with_browser_navigation method specifically.
"""

import os
import sys
from sync_script import SubsplashSyncService

def test_browser_navigation():
    """Test the browser navigation method from sync_script.py"""
    print("🧪 Testing browser navigation method from sync_script.py...")
    print("=" * 60)
    
    # Create service instance
    service = SubsplashSyncService()
    
    # Test the browser navigation method directly
    print("🌐 Calling _scrape_calendar_with_browser_navigation()...")
    events = service._scrape_calendar_with_browser_navigation()
    
    if events:
        print(f"\n✅ SUCCESS! Found {len(events)} events using browser navigation")
        
        # Show some sample events
        print("\n📅 Sample events found:")
        for i, event in enumerate(events[:5]):  # Show first 5 events
            print(f"  {i+1}. {event.get('title', 'No title')} - {event.get('date', 'No date')}")
        
        # Show date range
        if len(events) > 5:
            print(f"  ... and {len(events) - 5} more events")
        
        # Analyze date distribution
        dates = [event.get('date') for event in events if event.get('date')]
        if dates:
            min_date = min(dates)
            max_date = max(dates)
            print(f"\n📊 Date range: {min_date} to {max_date}")
        
        return True
    else:
        print("❌ FAILED! No events found using browser navigation")
        return False

if __name__ == "__main__":
    try:
        success = test_browser_navigation()
        if success:
            print("\n🎉 Test completed successfully!")
            sys.exit(0)
        else:
            print("\n💥 Test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test crashed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
