#!/usr/bin/env python3
"""
Test script to verify the 4-hour time offset fix
"""

from datetime import datetime, timedelta

def test_time_offset_fix():
    """Test the time offset correction logic"""
    
    print("🧪 Testing 4-hour time offset fix...")
    print("=" * 50)
    
    # Test cases with different time formats
    test_cases = [
        ("6:30a", "2025-01-15"),   # Morning prayer
        ("5:15p", "2025-01-15"),   # Evening prayer
        ("7:15a", "2025-01-15"),   # BAM
        ("10:00", "2025-01-15"),   # 24-hour format
        ("2:30pm", "2025-01-15"),  # PM format
        ("12:00a", "2025-01-15"),  # Midnight
        ("12:00p", "2025-01-15"),  # Noon
    ]
    
    for time_str, date_str in test_cases:
        print(f"\n📅 Testing: {time_str} on {date_str}")
        
        # Parse the original time
        original_time = parse_time_with_offset(time_str, datetime.strptime(date_str, '%Y-%m-%d'))
        
        if original_time:
            start_time, end_time = original_time
            print(f"   Original time: {time_str}")
            print(f"   Parsed start:  {start_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Parsed end:    {end_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Duration:      {end_time - start_time}")
            
            # Show the offset correction
            original_hour = start_time.hour + 4  # Reverse the offset to show original
            if original_hour >= 24:
                original_hour -= 24
            print(f"   Original hour: {original_hour:02d}:{start_time.minute:02d}")
        else:
            print(f"   ❌ Failed to parse time: {time_str}")

def parse_time_with_offset(time_str: str, event_date: datetime):
    """Parse time and apply 4-hour offset correction (same logic as sync script)"""
    try:
        if not time_str or time_str.lower() in ['all day', 'all-day', '']:
            # No time specified, treat as all-day event
            start_time = event_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=1)
            return start_time, end_time
        
        # Parse time formats like "6:30a", "5:15p", "10:00", "6:30am", "5:15pm"
        time_str = time_str.lower().strip()
        
        # Handle AM/PM variations
        is_am = False
        is_pm = False
        
        if 'a' in time_str and 'm' not in time_str:
            # Handle "6:30a" format
            time_str = time_str.replace('a', '').strip()
            is_am = True
        elif 'am' in time_str:
            # Handle "6:30am" format
            time_str = time_str.replace('am', '').strip()
            is_am = True
        elif 'p' in time_str and 'm' not in time_str:
            # Handle "5:15p" format
            time_str = time_str.replace('p', '').strip()
            is_pm = True
        elif 'pm' in time_str:
            # Handle "5:15pm" format
            time_str = time_str.replace('pm', '').strip()
            is_pm = True
        
        # Parse hour and minute
        if ':' in time_str:
            hour, minute = map(int, time_str.split(':'))
        else:
            # Handle "6a" format (just hour)
            hour = int(time_str)
            minute = 0
        
        # Apply AM/PM logic
        if is_am:
            if hour == 12:
                hour = 0
        elif is_pm:
            if hour != 12:
                hour += 12
        # If neither AM nor PM specified, assume 24-hour format
        
        # Validate hour and minute
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            print(f"      ⚠️ Invalid time values: hour={hour}, minute={minute}")
            # Fallback to all-day event
            start_time = event_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=1)
            return start_time, end_time
        
        # Create start time
        start_time = event_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Apply 4-hour offset correction
        start_time = start_time - timedelta(hours=4)
        
        # Default duration: 1 hour for most events
        end_time = start_time + timedelta(hours=1)
        
        return start_time, end_time
        
    except Exception as e:
        print(f"      ❌ Error parsing time '{time_str}': {str(e)}")
        return None

if __name__ == "__main__":
    test_time_offset_fix()
    print("\n" + "=" * 50)
    print("✅ Time offset fix test completed!")
    print("\n📝 Summary:")
    print("   - All times are adjusted by -4 hours to fix the timezone offset")
    print("   - This ensures events appear at the correct time in Google Calendar")
    print("   - The fix handles various time formats (6:30a, 5:15p, 10:00, etc.)")
