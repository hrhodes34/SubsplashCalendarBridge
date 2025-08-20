#!/usr/bin/env python3
"""
Test script for the improved Subsplash scraping functionality
"""

import sys
import os

# Add the current directory to the path so we can import the sync script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sync_script import SubsplashSyncService

def test_scraping():
    """Test the scraping functionality"""
    print("🧪 Testing enhanced Subsplash calendar scraping...")
    print("🔍 This will try multiple strategies including systematic month-by-month scraping...")
    print("📅 The script will continue until it finds 3 consecutive empty months")
    
    # Create service instance
    service = SubsplashSyncService()
    
    # Test the scraping
    try:
        events = service.scrape_subsplash_events()
        
        if events:
            print(f"\n✅ Successfully scraped {len(events)} events!")
            
            # Show event distribution
            print("\n📊 Event Distribution:")
            from datetime import datetime
            current_date = datetime.now()
            
            # Group events by month
            monthly_events = {}
            for event in events:
                if 'start' in event and event['start']:
                    month_key = event['start'].strftime('%Y-%m')
                    if month_key not in monthly_events:
                        monthly_events[month_key] = []
                    monthly_events[month_key].append(event)
            
            # Show events by month
            sorted_months = sorted(monthly_events.keys())
            for month in sorted_months:
                month_date = datetime.strptime(month, '%Y-%m')
                month_name = month_date.strftime('%B %Y')
                event_count = len(monthly_events[month])
                print(f"  📅 {month_name}: {event_count} events")
            
            print(f"\n📅 Events found:")
            for i, event in enumerate(events[:10], 1):  # Show first 10 events
                print(f"  {i}. {event['title']}")
                print(f"     Date: {event['start'].strftime('%B %d, %Y at %I:%M %p')}")
                if event.get('description'):
                    desc = event['description'][:100] + "..." if len(event['description']) > 100 else event['description']
                    print(f"     Description: {desc}")
                if event.get('source'):
                    print(f"     Source: {event['source']}")
                print()

            if len(events) > 10:
                print(f"  ... and {len(events) - 10} more events")
        else:
            print("❌ No events found")

    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scraping()
