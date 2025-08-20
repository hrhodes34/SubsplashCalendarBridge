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
    
    # Create service instance
    service = SubsplashSyncService()
    
    # Test the scraping
    try:
        events = service.scrape_subsplash_events()
        
        if events:
            print(f"\n✅ Successfully scraped {len(events)} events!")
            print("\n📅 Events found:")
            for i, event in enumerate(events[:10], 1):  # Show first 10 events
                print(f"  {i}. {event['title']}")
                print(f"     Date: {event['start'].strftime('%B %d, %Y at %I:%M %p')}")
                if event.get('description'):
                    desc = event['description'][:100] + "..." if len(event['description']) > 100 else event['description']
                    print(f"     Description: {desc}")
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
