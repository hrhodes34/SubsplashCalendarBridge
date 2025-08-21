#!/usr/bin/env python3
"""
Test script to verify timezone conversion handles Daylight Saving Time correctly
This tests both EDT (summer) and EST (winter) conversions
"""

import os
import sys
from datetime import datetime
import pytz
import re

def parse_and_convert_time_for_date(time_str: str, target_date: datetime) -> datetime:
    """Parse time string and apply timezone conversion for a specific date"""
    try:
        # Parse time string - handle both formats
        original_time = time_str
        time_str = time_str.lower()
        
        # Handle different time formats
        if time_str.endswith('p') and not time_str.endswith('pm'):
            time_str = time_str[:-1] + 'pm'
        elif time_str.endswith('a') and not time_str.endswith('am'):
            time_str = time_str[:-1] + 'am'
        
        # Try different time formats
        time_formats = [
            '%I:%M%p',  # 9:15pm
            '%I:%M %p', # 9:15 pm
            '%H:%M',    # 21:15
        ]
        
        parsed_time = None
        for fmt in time_formats:
            try:
                parsed_time = datetime.strptime(time_str, fmt)
                break
            except ValueError:
                continue
        
        if not parsed_time:
            print(f"Could not parse time: {time_str}")
            return None
        
        # Apply timezone conversion (fix for 4-hour offset)
        # The scraper pulls times in UTC, but they display as if they're Eastern Time
        # So we need to convert FROM UTC TO Eastern Time (subtract 4/5 hours depending on DST)
        utc_tz = pytz.timezone('UTC')
        est_tz = pytz.timezone('US/Eastern')
        
        # Create a datetime object for the target date with the parsed time
        event_datetime = datetime.combine(target_date.date(), parsed_time.time())
        
        # First, treat the time as UTC (this is what the scraper actually gets)
        utc_datetime = utc_tz.localize(event_datetime)
        
        # Then convert to Eastern Time (this subtracts 4 hours during EDT, 5 hours during EST)
        eastern_datetime = utc_datetime.astimezone(est_tz)
        
        print(f"Time conversion: {original_time} UTC -> {utc_datetime} -> {eastern_datetime} Eastern")
        
        return eastern_datetime
        
    except Exception as e:
        print(f"Error parsing/converting time {time_str}: {str(e)}")
        return None

def test_dst_conversion():
    """Test the timezone conversion for both summer (EDT) and winter (EST)"""
    print("🧪 Testing Daylight Saving Time conversion...")
    print("=" * 60)
    
    # Test dates
    summer_date = datetime(2025, 8, 21)  # August - EDT (UTC-4)
    winter_date = datetime(2025, 12, 21)  # December - EST (UTC-5)
    
    test_times = ["9:15p", "10:30a"]
    
    for time_str in test_times:
        print(f"\nTesting time: {time_str}")
        print("-" * 30)
        
        # Test summer (EDT - UTC-4)
        print(f"Summer (August) - EDT (UTC-4):")
        summer_result = parse_and_convert_time_for_date(time_str, summer_date)
        if summer_result:
            summer_eastern = summer_result.astimezone(pytz.timezone('US/Eastern'))
            print(f"  Result: {summer_eastern.strftime('%I:%M %p %Z')} ({summer_eastern.strftime('%z')})")
            
            # Verify EDT offset (UTC-4)
            if "9:15" in time_str and "p" in time_str.lower():
                expected_hour = 17  # 9 PM UTC - 4 hours = 5 PM EDT
                if summer_eastern.hour == expected_hour:
                    print(f"  ✅ EDT conversion verified: 9:15 PM UTC -> 5:15 PM EDT")
                else:
                    print(f"  ❌ EDT conversion failed: Expected 5:15 PM, got {summer_eastern.strftime('%I:%M %p')}")
            elif "10:30" in time_str and "a" in time_str.lower():
                expected_hour = 6  # 10:30 AM UTC - 4 hours = 6:30 AM EDT
                if summer_eastern.hour == expected_hour:
                    print(f"  ✅ EDT conversion verified: 10:30 AM UTC -> 6:30 AM EDT")
                else:
                    print(f"  ❌ EDT conversion failed: Expected 6:30 AM, got {summer_eastern.strftime('%I:%M %p')}")
        
        # Test winter (EST - UTC-5)
        print(f"\nWinter (December) - EST (UTC-5):")
        winter_result = parse_and_convert_time_for_date(time_str, winter_date)
        if winter_result:
            winter_eastern = winter_result.astimezone(pytz.timezone('US/Eastern'))
            print(f"  Result: {winter_eastern.strftime('%I:%M %p %Z')} ({winter_eastern.strftime('%z')})")
            
            # Verify EST offset (UTC-5)
            if "9:15" in time_str and "p" in time_str.lower():
                expected_hour = 16  # 9 PM UTC - 5 hours = 4 PM EST
                if winter_eastern.hour == expected_hour:
                    print(f"  ✅ EST conversion verified: 9:15 PM UTC -> 4:15 PM EST")
                else:
                    print(f"  ❌ EST conversion failed: Expected 4:15 PM, got {winter_eastern.strftime('%I:%M %p')}")
            elif "10:30" in time_str and "a" in time_str.lower():
                expected_hour = 5  # 10:30 AM UTC - 5 hours = 5:30 AM EST
                if winter_eastern.hour == expected_hour:
                    print(f"  ✅ EST conversion verified: 10:30 AM UTC -> 5:30 AM EST")
                else:
                    print(f"  ❌ EST conversion failed: Expected 5:30 AM, got {winter_eastern.strftime('%I:%M %p')}")
        
        print()
    
    print("=" * 60)
    print("🎯 DST conversion test completed!")
    print("\nSummary:")
    print("• Summer (EDT): UTC - 4 hours")
    print("• Winter (EST): UTC - 5 hours")
    print("• pytz automatically handles the DST transition")

if __name__ == "__main__":
    test_dst_conversion()
