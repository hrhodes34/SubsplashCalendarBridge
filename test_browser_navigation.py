#!/usr/bin/env python3
"""
Test script specifically for the new browser-based calendar navigation
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sync_script import SubsplashSyncService
import traceback

def test_browser_navigation():
    """Test the browser-based month-by-month navigation specifically"""
    print("🌐 Testing Browser-Based Month-by-Month Navigation")
    print("=" * 60)
    print("This will open a Chrome browser and click navigation arrows!")
    print()
    
    try:
        # Create the service
        service = SubsplashSyncService()
        
        # Test just the browser navigation method directly
        print("🔍 Calling _scrape_calendar_with_browser_navigation()...")
        browser_events = service._scrape_calendar_with_browser_navigation()
        
        if browser_events:
            print(f"\n🎉 SUCCESS! Browser navigation found {len(browser_events)} events!")
            
            # Show the events found
            print("\n📅 Events found through browser navigation:")
            for i, event in enumerate(browser_events[:10]):  # Show first 10
                print(f"  {i+1}. {event.get('title', 'Unknown')} - {event.get('date', 'Unknown date')}")
            
            if len(browser_events) > 10:
                print(f"  ... and {len(browser_events) - 10} more events")
                
            # Find the latest event
            latest_date = None
            latest_event = None
            for event in browser_events:
                event_date = event.get('date')
                if event_date and (latest_date is None or event_date > latest_date):
                    latest_date = event_date
                    latest_event = event
            
            if latest_event:
                print(f"\n🚀 LATEST EVENT FOUND: {latest_event.get('title')} on {latest_date}")
                print("This should be MUCH further out than September 13th!")
            
        else:
            print("\n❌ No events found through browser navigation")
            print("This could mean:")
            print("- The calendar structure is different than expected")
            print("- Chrome driver needs setup")
            print("- Navigation arrows are structured differently")
        
    except Exception as e:
        print(f"\n❌ Error during browser navigation test: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        
        print("\n🔧 Possible solutions:")
        print("- Ensure Chrome browser is installed")
        print("- Check internet connection")
        print("- Try running as administrator")

if __name__ == "__main__":
    test_browser_navigation()
