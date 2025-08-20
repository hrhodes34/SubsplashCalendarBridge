#!/usr/bin/env python3
"""
Test script to check if events from browser navigation have the correct format for Google Calendar sync.
"""

import os
import sys
from sync_script import SubsplashSyncService

def test_event_format():
    """Test that browser navigation events have the correct format"""
    print("🧪 Testing event format from browser navigation...")
    print("=" * 60)
    
    # Create service instance
    service = SubsplashSyncService()
    
    # Get just a few events to check format
    print("🌐 Getting events from browser navigation...")
    events = service._scrape_calendar_with_browser_navigation()
    
    if not events:
        print("❌ No events found")
        return False
    
    print(f"✅ Found {len(events)} events")
    
    # Check the format of the first few events
    print("\n📋 Checking event format:")
    for i, event in enumerate(events[:3]):
        print(f"\nEvent {i+1}:")
        print(f"  Title: {event.get('title', 'No title')}")
        print(f"  Start: {event.get('start', 'No start')}")
        print(f"  End: {event.get('end', 'No end')}")
        print(f"  All day: {event.get('all_day', 'No all_day')}")
        print(f"  Source: {event.get('source', 'No source')}")
        
        # Check if it has the required fields for Google Calendar sync
        has_start = 'start' in event
        has_end = 'end' in event
        has_title = 'title' in event
        
        print(f"  ✅ Has start: {has_start}")
        print(f"  ✅ Has end: {has_end}")
        print(f"  ✅ Has title: {has_title}")
        
        if has_start and has_end and has_title:
            print(f"  🎯 Event format is CORRECT for Google Calendar sync!")
        else:
            print(f"  ❌ Event format is INCORRECT for Google Calendar sync!")
    
    # Check if all events have the correct format
    correct_format_count = 0
    for event in events:
        if 'start' in event and 'end' in event and 'title' in event:
            correct_format_count += 1
    
    print(f"\n📊 Format Summary:")
    print(f"  Total events: {len(events)}")
    print(f"  Correct format: {correct_format_count}")
    print(f"  Incorrect format: {len(events) - correct_format_count}")
    
    if correct_format_count == len(events):
        print("🎉 ALL events have the correct format!")
        return True
    else:
        print("⚠️ Some events have incorrect format")
        return False

if __name__ == "__main__":
    try:
        success = test_event_format()
        if success:
            print("\n🎉 Event format test passed!")
            sys.exit(0)
        else:
            print("\n💥 Event format test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test crashed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
