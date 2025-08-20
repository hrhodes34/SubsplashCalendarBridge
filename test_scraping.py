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
    print("🧪 Testing improved Subsplash scraping...")
    print("🔍 This will try multiple strategies to find events further into the future...")
    
    # Create service instance
    service = SubsplashSyncService()
    
    # Test the scraping
    try:
        events = service.scrape_subsplash_events()
        
        if events:
            print(f"\n✅ Successfully scraped {len(events)} events!")
            
            # Show date range
            start_dates = [event['start'] for event in events if 'start' in event and event['start']]
            if start_dates:
                earliest = min(start_dates)
                latest = max(start_dates)
                print(f"📅 Date range: {earliest.strftime('%B %d, %Y')} to {latest.strftime('%B %d, %Y')}")
                
                # Calculate months ahead
                from datetime import datetime
                now = datetime.now()
                months_ahead = ((latest.year - now.year) * 12) + (latest.month - now.month)
                print(f"📅 Events extend {months_ahead} months into the future")
            
            print("\n📅 Events found:")
            # Sort events by date
            sorted_events = sorted(events, key=lambda x: x['start'] if 'start' in x and x['start'] else datetime.min)
            
            for i, event in enumerate(sorted_events[:15], 1):  # Show first 15 events
                print(f"  {i}. {event['title']}")
                if 'start' in event and event['start']:
                    print(f"     Date: {event['start'].strftime('%B %d, %Y at %I:%M %p')}")
                if event.get('description'):
                    desc = event['description'][:100] + "..." if len(event['description']) > 100 else event['description']
                    print(f"     Description: {desc}")
                print()
            
            if len(events) > 15:
                print(f"  ... and {len(events) - 15} more events")
                
            # Show events by month
            print("📊 Events by month:")
            monthly_counts = {}
            for event in events:
                if 'start' in event and event['start']:
                    month_key = event['start'].strftime('%B %Y')
                    monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
            
            sorted_months = sorted(monthly_counts.items(), key=lambda x: datetime.strptime(x[0], '%B %Y'))
            for month, count in sorted_months:
                print(f"  {month}: {count} events")
                
        else:
            print("❌ No events found")
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scraping()
