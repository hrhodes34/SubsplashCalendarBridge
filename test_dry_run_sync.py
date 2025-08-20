#!/usr/bin/env python3
"""
Dry-run test script for Subsplash Calendar Bridge sync.
This script simulates the full sync process without actually modifying live calendars,
allowing you to see exactly what would be synced and verify all the data.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from sync_script import SubsplashSyncService, get_enabled_calendars

class DryRunSyncService(SubsplashSyncService):
    """Extended service class that simulates sync without making changes"""
    
    def __init__(self, target_calendar=None):
        super().__init__(target_calendar)
        self.dry_run = True
        self.simulated_events = []
        self.simulated_changes = []
    
    def sync_to_google_calendar(self, events):
        """Simulate sync to Google Calendar without making actual changes"""
        print(f"🔍 DRY RUN: Simulating sync of {len(events)} events to Google Calendar")
        print(f"📅 Target Calendar: {self.target_calendar['name']}")
        print(f"🆔 Calendar ID: {self.target_calendar['google_calendar_id']}")
        
        self.simulated_events = events
        self.simulated_changes = []
        
        # Simulate what would happen during sync
        for event in events:
            change_type = self._simulate_event_sync(event)
            self.simulated_changes.append(change_type)
        
        print(f"✅ DRY RUN COMPLETE: Would sync {len(events)} events")
        return True
    
    def _simulate_event_sync(self, event):
        """Simulate what would happen when syncing a single event"""
        event_id = event.get('id', 'new_event')
        title = event.get('title', 'No Title')
        date = event.get('date', 'No Date')
        time = event.get('time', 'No Time')
        
        # Determine if this would be a new event or update
        if event_id == 'new_event':
            change_type = f"➕ CREATE: {title} on {date} at {time}"
        else:
            change_type = f"🔄 UPDATE: {title} on {date} at {time}"
        
        return change_type

def run_dry_run_sync(calendar_key=None):
    """Run a dry-run sync for testing purposes"""
    print("🧪 Starting DRY RUN Sync Test...")
    print("=" * 80)
    print("This will simulate the sync process WITHOUT modifying live calendars")
    print("=" * 80)
    
    enabled_calendars = get_enabled_calendars()
    if not enabled_calendars:
        print("❌ No enabled calendars found!")
        return False
    
    if calendar_key and calendar_key in enabled_calendars:
        calendars_to_test = {calendar_key: enabled_calendars[calendar_key]}
    else:
        calendars_to_test = enabled_calendars
    
    all_results = {}
    
    for cal_key, cal_config in calendars_to_test.items():
        print(f"\n{'='*60}")
        print(f"🔄 DRY RUN SYNC: {cal_config['name']}")
        print(f"{'='*60}")
        
        try:
            # Create dry-run service
            service = DryRunSyncService(cal_config)
            
            # Test authentication
            print("🔐 Testing Google Calendar authentication...")
            if not service.authenticate_google():
                print("❌ Authentication failed - skipping this calendar")
                all_results[cal_key] = {'success': False, 'error': 'Authentication failed'}
                continue
            
            # Scrape events
            print("🌐 Scraping Subsplash events...")
            events = service.scrape_subsplash_events()
            
            if not events:
                print("❌ No events found from Subsplash")
                all_results[cal_key] = {'success': False, 'error': 'No events found', 'count': 0}
                continue
            
            print(f"✅ Found {len(events)} events from Subsplash")
            
            # Simulate sync
            print("🔄 Simulating sync to Google Calendar...")
            sync_success = service.sync_to_google_calendar(events)
            
            if sync_success:
                # Show detailed results
                print(f"\n📊 DRY RUN RESULTS for {cal_config['name']}:")
                print(f"   Total events found: {len(events)}")
                print(f"   Events that would be synced: {len(service.simulated_changes)}")
                
                # Show sample events with details
                print(f"\n📋 Sample events that would be synced:")
                for i, event in enumerate(events[:5]):  # Show first 5 events
                    print(f"   {i+1}. {event.get('title', 'No title')}")
                    print(f"      📅 Date: {event.get('date', 'No date')}")
                    print(f"      🕐 Time: {event.get('time', 'No time')}")
                    print(f"      📍 Location: {event.get('location', 'No location')}")
                    print(f"      📝 Description: {event.get('description', 'No description')[:100]}...")
                    print()
                
                # Show date analysis
                date_analysis = analyze_event_dates(events)
                print(f"📅 Date Analysis:")
                print(f"   Earliest event: {date_analysis['earliest_date']}")
                print(f"   Latest event: {date_analysis['latest_date']}")
                print(f"   Date range: {date_analysis['date_range_days']} days")
                print(f"   Events with valid dates: {date_analysis['events_with_dates']}/{len(events)}")
                
                # Show what would happen during sync
                print(f"\n🔄 Sync Simulation Results:")
                for i, change in enumerate(service.simulated_changes[:10]):  # Show first 10 changes
                    print(f"   {i+1}. {change}")
                
                if len(service.simulated_changes) > 10:
                    print(f"   ... and {len(service.simulated_changes) - 10} more changes")
                
                all_results[cal_key] = {
                    'success': True,
                    'count': len(events),
                    'date_analysis': date_analysis,
                    'sample_events': events[:3],
                    'sync_changes': service.simulated_changes
                }
                
            else:
                print("❌ Sync simulation failed")
                all_results[cal_key] = {'success': False, 'error': 'Sync simulation failed'}
                
        except Exception as e:
            print(f"💥 Error during dry-run sync: {str(e)}")
            all_results[cal_key] = {'success': False, 'error': str(e)}
    
    return all_results

def analyze_event_dates(events):
    """Analyze event dates for consistency and range"""
    if not events:
        return None
    
    dates = []
    for event in events:
        date_str = event.get('date')
        if date_str:
            try:
                # Try to parse the date
                parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                dates.append(parsed_date)
            except ValueError:
                # Try alternative date formats
                try:
                    parsed_date = datetime.strptime(date_str, '%m/%d/%Y')
                    dates.append(parsed_date)
                except ValueError:
                    try:
                        parsed_date = datetime.strptime(date_str, '%d/%m/%Y')
                        dates.append(parsed_date)
                    except ValueError:
                        continue
    
    if not dates:
        return {
            'earliest_date': 'None',
            'latest_date': 'None',
            'date_range_days': 0,
            'events_with_dates': 0
        }
    
    earliest = min(dates)
    latest = max(dates)
    date_range = (latest - earliest).days
    
    return {
        'earliest_date': earliest.strftime('%Y-%m-%d'),
        'latest_date': latest.strftime('%Y-%m-%d'),
        'date_range_days': date_range,
        'events_with_dates': len(dates)
    }

def main():
    """Main function for dry-run testing"""
    print("🚀 Subsplash Calendar Bridge - DRY RUN SYNC TEST")
    print("=" * 80)
    
    # Check if user wants to test specific calendar
    if len(sys.argv) > 1:
        calendar_key = sys.argv[1].lower()
        print(f"🎯 Testing specific calendar: {calendar_key}")
        results = run_dry_run_sync(calendar_key)
    else:
        print("🔄 Testing all enabled calendars...")
        results = run_dry_run_sync()
    
    # Summary
    print("\n" + "="*80)
    print("📊 DRY RUN TEST SUMMARY")
    print("=" * 80)
    
    total_events = 0
    successful_calendars = 0
    
    for calendar_key, result in results.items():
        if result.get('success'):
            successful_calendars += 1
            event_count = result.get('count', 0)
            total_events += event_count
            print(f"✅ {calendar_key.upper()}: {event_count} events would be synced")
        else:
            error = result.get('error', 'Unknown error')
            print(f"❌ {calendar_key.upper()}: Failed - {error}")
    
    print(f"\n📈 Overall Results:")
    print(f"   Successful calendars: {successful_calendars}/{len(results)}")
    print(f"   Total events that would be synced: {total_events}")
    
    if successful_calendars == len(results):
        print("\n🎉 DRY RUN COMPLETE! All calendars are ready for sync.")
        print("💡 To run the actual sync, use: python sync_script.py")
    else:
        print("\n⚠️ Some calendars had issues. Please review the errors above.")
    
    return successful_calendars == len(results)

if __name__ == "__main__":
    try:
        success = main()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Dry-run test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Dry-run test crashed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
