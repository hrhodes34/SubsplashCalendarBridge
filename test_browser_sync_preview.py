#!/usr/bin/env python3
"""
Simple test to show what events would be synced to Google Calendar
using the browser navigation method that we know works.
"""

import os
import sys
from sync_script import SubsplashSyncService, get_enabled_calendars

def test_browser_sync_preview():
    """Test what events would be synced using browser navigation"""
    print("🔍 Testing Browser Navigation Sync Preview...")
    print("=" * 60)
    
    enabled_calendars = get_enabled_calendars()
    if not enabled_calendars:
        print("❌ No enabled calendars found!")
        return False
    
    # Test with BAM calendar first
    bam_calendar = enabled_calendars.get('bam')
    if not bam_calendar:
        print("❌ BAM calendar not found!")
        return False
    
    print(f"🎯 Testing with: {bam_calendar['name']}")
    print(f"📍 URL: {bam_calendar['subsplash_url']}")
    print(f"📅 Google Calendar ID: {bam_calendar['google_calendar_id']}")
    print()
    
    try:
        # Create service
        service = SubsplashSyncService(bam_calendar)
        
        # Test authentication
        print("🔐 Testing Google Calendar authentication...")
        if not service.authenticate_google():
            print("❌ Authentication failed!")
            return False
        
        print("✅ Authentication successful!")
        print()
        
        # Use browser navigation method directly
        print("🌐 Using browser navigation to find events...")
        print("(This will take a moment as it navigates month by month)")
        print()
        
        # Add debug output to see events as they're found
        print("🔍 DEBUG: Starting browser navigation...")
        print("🔍 DEBUG: This will show events as they're discovered month by month")
        print()
        
        events = service._scrape_calendar_with_browser_navigation()
        
        if events:
            print(f"\n🎉 SUCCESS! Found {len(events)} events using browser navigation!")
            print()
            
            # Show what would be synced
            print("📋 EVENTS THAT WOULD BE SYNCED TO GOOGLE CALENDAR:")
            print("=" * 60)
            
            # Group events by month for better display
            events_by_month = {}
            for event in events:
                date_str = event.get('date', 'Unknown Date')
                month_key = date_str[:7] if date_str != 'Unknown Date' else 'Unknown'
                if month_key not in events_by_month:
                    events_by_month[month_key] = []
                events_by_month[month_key].append(event)
            
            # Display events by month
            for month in sorted(events_by_month.keys()):
                month_events = events_by_month[month]
                print(f"\n📅 {month} ({len(month_events)} events):")
                print("-" * 40)
                
                for i, event in enumerate(month_events[:10]):  # Show first 10 per month
                    title = event.get('title', 'No Title')
                    time = event.get('time', 'No Time')
                    location = event.get('location', 'No Location')
                    description = event.get('description', 'No Description')
                    
                    print(f"  {i+1}. {title}")
                    print(f"     🕐 {time}")
                    print(f"     📍 {location}")
                    if description and description != 'No Description':
                        desc_preview = description[:80] + "..." if len(description) > 80 else description
                        print(f"     📝 {desc_preview}")
                    print()
                
                if len(month_events) > 10:
                    print(f"     ... and {len(month_events) - 10} more events")
            
            print(f"\n📊 SUMMARY:")
            print(f"   Total events found: {len(events)}")
            print(f"   Months with events: {len(events_by_month)}")
            print(f"   Target calendar: {bam_calendar['name']}")
            print(f"   Google Calendar ID: {bam_calendar['google_calendar_id']}")
            
            print(f"\n✅ These {len(events)} events would be synced to your Google Calendar!")
            print(f"💡 To perform the actual sync, run: python sync_script.py")
            
            return True
            
        else:
            print("❌ No events found with browser navigation")
            return False
            
    except Exception as e:
        print(f"💥 Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_browser_sync_preview()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test crashed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
