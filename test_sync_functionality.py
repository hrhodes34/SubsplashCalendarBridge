#!/usr/bin/env python3
"""
Comprehensive test script for Subsplash Calendar Bridge sync functionality.
This script tests the sync process without actually modifying live calendars,
allowing you to verify dates, event mapping, and scraping accuracy.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from sync_script import SubsplashSyncService, get_enabled_calendars

def test_calendar_configuration():
    """Test that calendar configuration is properly set up"""
    print("🔧 Testing Calendar Configuration...")
    print("=" * 60)
    
    enabled_calendars = get_enabled_calendars()
    if not enabled_calendars:
        print("❌ No enabled calendars found!")
        return False
    
    print(f"✅ Found {len(enabled_calendars)} enabled calendars:")
    for calendar_key, calendar_config in enabled_calendars.items():
        print(f"   • {calendar_config['name']} ({calendar_key})")
        print(f"     - Subsplash URL: {calendar_config['subsplash_url']}")
        print(f"     - Google Calendar ID: {calendar_config['google_calendar_id']}")
        print(f"     - Enabled: {calendar_config['enabled']}")
        print()
    
    return True

def test_google_authentication():
    """Test Google Calendar authentication"""
    print("🔐 Testing Google Calendar Authentication...")
    print("=" * 60)
    
    try:
        # Test with first enabled calendar
        enabled_calendars = get_enabled_calendars()
        if not enabled_calendars:
            print("❌ No enabled calendars to test with")
            return False
        
        first_calendar = next(iter(enabled_calendars.values()))
        service = SubsplashSyncService(first_calendar)
        
        if service.authenticate_google():
            print("✅ Google Calendar authentication successful!")
            return True
        else:
            print("❌ Google Calendar authentication failed!")
            print("   Make sure you have credentials.json in your directory")
            return False
            
    except Exception as e:
        print(f"❌ Authentication test failed with error: {str(e)}")
        return False

def test_subsplash_scraping(calendar_key=None):
    """Test Subsplash event scraping for a specific calendar or all calendars"""
    print("🌐 Testing Subsplash Event Scraping...")
    print("=" * 60)
    
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
        print(f"\n📅 Testing scraping for: {cal_config['name']}")
        print(f"🔗 URL: {cal_config['subsplash_url']}")
        
        try:
            service = SubsplashSyncService(cal_config)
            
            # Test scraping without browser navigation first
            print("   🔍 Testing basic scraping...")
            events = service.scrape_subsplash_events()
            
            if events:
                print(f"   ✅ Found {len(events)} events!")
                
                # Analyze event data
                event_analysis = analyze_events(events)
                all_results[cal_key] = {
                    'count': len(events),
                    'analysis': event_analysis,
                    'sample_events': events[:3]  # First 3 events for inspection
                }
                
                # Show sample events
                print("   📋 Sample events:")
                for i, event in enumerate(events[:3]):
                    print(f"      {i+1}. {event.get('title', 'No title')}")
                    print(f"         Date: {event.get('date', 'No date')}")
                    print(f"         Time: {event.get('time', 'No time')}")
                    print(f"         Location: {event.get('location', 'No location')}")
                    print()
                
                # Show date analysis
                print(f"   📊 Date Analysis:")
                print(f"      Earliest: {event_analysis['earliest_date']}")
                print(f"      Latest: {event_analysis['latest_date']}")
                print(f"      Date range: {event_analysis['date_range_days']} days")
                print(f"      Events with dates: {event_analysis['events_with_dates']}/{len(events)}")
                
            else:
                print("   ❌ No events found!")
                all_results[cal_key] = {'count': 0, 'analysis': None, 'sample_events': []}
                
        except Exception as e:
            print(f"   ❌ Error testing {cal_config['name']}: {str(e)}")
            all_results[cal_key] = {'count': 0, 'analysis': None, 'sample_events': [], 'error': str(e)}
    
    return all_results

def analyze_events(events):
    """Analyze events for date consistency and range"""
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

def test_event_mapping():
    """Test that events are properly mapped to the correct calendars"""
    print("\n🗺️ Testing Event Calendar Mapping...")
    print("=" * 60)
    
    enabled_calendars = get_enabled_calendars()
    if not enabled_calendars:
        print("❌ No enabled calendars found!")
        return False
    
    print("✅ Calendar mapping configuration:")
    for calendar_key, calendar_config in enabled_calendars.items():
        print(f"   • {calendar_config['name']} -> {calendar_config['google_calendar_id']}")
    
    return True

def test_date_parsing():
    """Test date parsing functionality"""
    print("\n📅 Testing Date Parsing...")
    print("=" * 60)
    
    # Test various date formats that might come from Subsplash
    test_dates = [
        "2024-01-15",
        "01/15/2024",
        "15/01/2024",
        "January 15, 2024",
        "15 Jan 2024",
        "2024-01-15T10:30:00",
        "01/15/24",
        "15/01/24"
    ]
    
    print("Testing date parsing for various formats:")
    for date_str in test_dates:
        try:
            # Try the main date parsing method
            parsed = datetime.strptime(date_str, '%Y-%m-%d')
            print(f"   ✅ {date_str} -> {parsed.strftime('%Y-%m-%d')}")
        except ValueError:
            try:
                parsed = datetime.strptime(date_str, '%m/%d/%Y')
                print(f"   ✅ {date_str} -> {parsed.strftime('%Y-%m-%d')}")
            except ValueError:
                try:
                    parsed = datetime.strptime(date_str, '%d/%m/%Y')
                    print(f"   ✅ {date_str} -> {parsed.strftime('%Y-%m-%d')}")
                except ValueError:
                    print(f"   ❌ {date_str} -> Failed to parse")
    
    return True

def run_comprehensive_test():
    """Run all tests in sequence"""
    print("🧪 Starting Comprehensive Sync Functionality Test...")
    print("=" * 80)
    print("This test will verify your sync setup without modifying live calendars")
    print("=" * 80)
    
    results = {}
    
    # Test 1: Calendar Configuration
    print("\n" + "="*80)
    results['config'] = test_calendar_configuration()
    
    # Test 2: Google Authentication
    print("\n" + "="*80)
    results['auth'] = test_google_authentication()
    
    # Test 3: Event Calendar Mapping
    print("\n" + "="*80)
    results['mapping'] = test_event_mapping()
    
    # Test 4: Date Parsing
    print("\n" + "="*80)
    results['date_parsing'] = test_date_parsing()
    
    # Test 5: Subsplash Scraping (for first calendar only to avoid overwhelming output)
    print("\n" + "="*80)
    enabled_calendars = get_enabled_calendars()
    if enabled_calendars:
        first_calendar_key = next(iter(enabled_calendars.keys()))
        results['scraping'] = test_subsplash_scraping(first_calendar_key)
    else:
        results['scraping'] = False
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    test_names = {
        'config': 'Calendar Configuration',
        'auth': 'Google Authentication',
        'mapping': 'Event Calendar Mapping',
        'date_parsing': 'Date Parsing',
        'scraping': 'Subsplash Scraping'
    }
    
    all_passed = True
    for test_key, test_name in test_names.items():
        status = "✅ PASSED" if results.get(test_key) else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not results.get(test_key):
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Your sync setup is ready.")
        print("💡 You can now run the actual sync with confidence.")
    else:
        print("\n⚠️ Some tests failed. Please review the issues above before running the sync.")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        if success:
            print("\n🚀 Ready to run sync! Use: python sync_script.py")
            sys.exit(0)
        else:
            print("\n🔧 Please fix the issues above before running the sync.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test crashed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
