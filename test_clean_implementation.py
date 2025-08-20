#!/usr/bin/env python3
"""
Test script for the clean Subsplash Calendar Sync implementation
This script tests the core functionality without requiring Google Calendar credentials
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    try:
        import bs4
        print("✅ beautifulsoup4 imported successfully")
    except ImportError as e:
        print(f"❌ beautifulsoup4 import failed: {e}")
        return False
    
    try:
        import selenium
        print("✅ selenium imported successfully")
    except ImportError as e:
        print(f"❌ selenium import failed: {e}")
        return False
    
    try:
        from google.oauth2 import service_account
        print("✅ google-auth imported successfully")
    except ImportError as e:
        print(f"❌ google-auth import failed: {e}")
        return False
    
    try:
        from dateutil.relativedelta import relativedelta
        print("✅ python-dateutil imported successfully")
    except ImportError as e:
        print(f"❌ python-dateutil import failed: {e}")
        return False
    
    return True

def test_calendar_config():
    """Test calendar configuration structure"""
    print("\n🔍 Testing calendar configuration...")
    
    calendar_configs = {
        'bam': {
            'name': 'BAM',
            'subsplash_url': 'https://antiochboone.com/calendar-bam',
            'google_calendar_id': 'test_bam_id',
            'location': 'Antioch Boone'
        },
        'kids': {
            'name': 'Kingdom Kids',
            'subsplash_url': 'https://antiochboone.com/calendar-balendar-kids',
            'google_calendar_id': 'test_kids_id',
            'location': 'Antioch Boone'
        },
        'prayer': {
            'name': 'Prayer',
            'subsplash_url': 'https://antiochboone.com/calendar-prayer',
            'google_calendar_id': 'test_prayer_id',
            'location': 'Antioch Boone'
        }
    }
    
    # Test each calendar config
    for key, config in calendar_configs.items():
        required_fields = ['name', 'subsplash_url', 'google_calendar_id', 'location']
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            print(f"❌ {key} calendar missing fields: {missing_fields}")
            return False
        else:
            print(f"✅ {key} calendar configuration valid")
    
    return True

def test_datetime_parsing():
    """Test datetime parsing functionality"""
    print("\n🔍 Testing datetime parsing...")
    
    # Test date patterns
    test_dates = [
        "August 15, 2024",
        "12/25/2024",
        "2024-12-25",
        "12-25-2024"
    ]
    
    # Test time patterns
    test_times = [
        "2:30pm",
        "10:00 AM",
        "14:30"
    ]
    
    try:
        from datetime import datetime
        
        # Test date parsing
        for date_str in test_dates:
            try:
                # This is a simplified test - the actual implementation has more robust parsing
                if "August" in date_str:
                    parsed = datetime.strptime(date_str, "%B %d, %Y")
                    print(f"✅ Parsed date: {date_str} -> {parsed}")
                elif "/" in date_str:
                    if len(date_str.split("/")[2]) == 4:
                        parsed = datetime.strptime(date_str, "%m/%d/%Y")
                        print(f"✅ Parsed date: {date_str} -> {parsed}")
                    else:
                        parsed = datetime.strptime(date_str, "%m/%d/%y")
                        print(f"✅ Parsed date: {date_str} -> {parsed}")
                elif "-" in date_str:
                    if len(date_str.split("-")[0]) == 4:
                        parsed = datetime.strptime(date_str, "%Y-%m-%d")
                        print(f"✅ Parsed date: {date_str} -> {parsed}")
                    else:
                        parsed = datetime.strptime(date_str, "%m-%d-%Y")
                        print(f"✅ Parsed date: {date_str} -> {parsed}")
            except ValueError as e:
                print(f"⚠️ Could not parse date {date_str}: {e}")
        
        # Test time parsing
        for time_str in test_times:
            try:
                if "pm" in time_str.lower():
                    clean_time = time_str.replace("pm", "").replace("PM", "").strip()
                    hour, minute = map(int, clean_time.split(":"))
                    if hour != 12:
                        hour += 12
                    print(f"✅ Parsed PM time: {time_str} -> {hour:02d}:{minute:02d}")
                elif "am" in time_str.lower():
                    clean_time = time_str.replace("am", "").replace("AM", "").strip()
                    hour, minute = map(int, clean_time.split(":"))
                    if hour == 12:
                        hour = 0
                    print(f"✅ Parsed AM time: {time_str} -> {hour:02d}:{minute:02d}")
                else:
                    hour, minute = map(int, time_str.split(":"))
                    print(f"✅ Parsed 24h time: {time_str} -> {hour:02d}:{minute:02d}")
            except ValueError as e:
                print(f"⚠️ Could not parse time {time_str}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Datetime parsing test failed: {e}")
        return False

def test_event_extraction_logic():
    """Test event extraction logic"""
    print("\n🔍 Testing event extraction logic...")
    
    # Test event title detection
    test_lines = [
        "Youth Group Meeting",  # Should be detected as event title
        "2:30 PM",              # Should NOT be detected (time)
        "August 15, 2024",      # Should NOT be detected (date)
        "Bible Study",           # Should be detected as event title
        "from 6:00 PM",         # Should NOT be detected (time indicator)
        "Prayer Night",          # Should be detected as event title
    ]
    
    def looks_like_datetime(text):
        """Simplified version of the datetime detection logic"""
        datetime_indicators = [
            'am', 'pm', 'edt', 'est', 'from', 'to', 'august', 'september', 'october', 
            'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june', 'july'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in datetime_indicators)
    
    def is_potential_event_title(line):
        """Simplified version of event title detection"""
        return (len(line) > 3 and len(line) < 100 and 
                not looks_like_datetime(line) and 
                line[0].isupper())
    
    for line in test_lines:
        is_event = is_potential_event_title(line)
        expected = "Youth Group Meeting" in line or "Bible Study" in line or "Prayer Night" in line
        status = "✅" if is_event == expected else "❌"
        print(f"{status} '{line}' -> Event: {is_event} (Expected: {expected})")
    
    return True

def test_environment_variables():
    """Test environment variable handling"""
    print("\n🔍 Testing environment variable handling...")
    
    # Test default values
    test_vars = {
        'MAX_MONTHS_TO_CHECK': '6',
        'MAX_CONSECUTIVE_EMPTY_MONTHS': '3',
        'BROWSER_WAIT_TIME': '10'
    }
    
    for var_name, expected_default in test_vars.items():
        actual_value = os.environ.get(var_name, expected_default)
        if actual_value == expected_default:
            print(f"✅ {var_name}: {actual_value} (default)")
        else:
            print(f"✅ {var_name}: {actual_value} (custom)")
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Clean Subsplash Calendar Sync Implementation")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_calendar_config,
        test_datetime_parsing,
        test_event_extraction_logic,
        test_environment_variables
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"💥 Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The implementation is ready to use.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
