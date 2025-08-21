#!/usr/bin/env python3
"""
Test script to verify timezone conversion logic
This tests the fix for the 4-hour offset issue from the working scraper
"""

import os
import sys
from datetime import datetime
import pytz
import re

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def parse_and_convert_time(time_str: str) -> datetime:
    """Parse time string and apply timezone conversion (fix for 4-hour offset)"""
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
        # So we need to convert FROM UTC TO Eastern Time (subtract 4 hours)
        utc_tz = pytz.timezone('UTC')
        est_tz = pytz.timezone('US/Eastern')
        
        # Create a datetime object for today with the parsed time
        today = datetime.now().date()
        event_datetime = datetime.combine(today, parsed_time.time())
        
        # First, treat the time as UTC (this is what the scraper actually gets)
        utc_datetime = utc_tz.localize(event_datetime)
        
        # Then convert to Eastern Time (this subtracts 4 hours during EDT)
        eastern_datetime = utc_datetime.astimezone(est_tz)
        
        print(f"Time conversion: {time_str} UTC -> {utc_datetime} -> {eastern_datetime} Eastern")
        
        return eastern_datetime
        
    except Exception as e:
        print(f"Error parsing/converting time {time_str}: {str(e)}")
        return None

def test_timezone_conversion():
    """Test the timezone conversion with the examples from your debug log"""
    print("🧪 Testing timezone conversion logic...")
    print("=" * 50)
    
    # Test cases from your debug log
    test_times = [
        "9:15p",    # Should become 9:15 PM EST -> 1:15 AM UTC (next day)
        "10:30a",   # Should become 10:30 AM EST -> 2:30 PM UTC
        "9:15pm",   # Alternative format
        "10:30am",  # Alternative format
    ]
    
    for time_str in test_times:
        print(f"\nTesting: {time_str}")
        result = parse_and_convert_time(time_str)
        
        if result:
            # Show the time in Eastern Time (this is what we want)
            est_time = result.astimezone(pytz.timezone('US/Eastern'))
            
            print(f"  Eastern Time: {est_time.strftime('%I:%M %p %Z')}")
            
            # Verify the timezone conversion (UTC to Eastern, -4 hours)
            if "9:15" in time_str and "p" in time_str.lower():
                # 9:15 PM UTC should become 5:15 PM Eastern Time
                expected_hour = 17  # 5 PM in 24-hour format
                if est_time.hour == expected_hour and est_time.minute == 15:
                    print(f"  ✅ Timezone conversion verified: 9:15 PM UTC -> 5:15 PM Eastern")
                else:
                    print(f"  ❌ Timezone conversion failed: Expected 5:15 PM, got {est_time.strftime('%I:%M %p')}")
            
            elif "10:30" in time_str and "a" in time_str.lower():
                # 10:30 AM UTC should become 6:30 AM Eastern Time
                expected_hour = 6  # 6:30 AM in 24-hour format
                if est_time.hour == expected_hour and est_time.minute == 30:
                    print(f"  ✅ Timezone conversion verified: 10:30 AM UTC -> 6:30 AM Eastern")
                else:
                    print(f"  ❌ Timezone conversion failed: Expected 6:30 AM, got {est_time.strftime('%I:%M %p')}")
        else:
            print(f"  ❌ Failed to parse/convert time: {time_str}")
    
    print("\n" + "=" * 50)
    print("🎯 Timezone conversion test completed!")

if __name__ == "__main__":
    test_timezone_conversion()
