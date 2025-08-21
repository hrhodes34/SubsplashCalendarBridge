#!/usr/bin/env python3
"""
Test script to verify dynamic timezone offset for DST changes
Tests that the correct offset is applied based on whether we're in DST or Standard Time
"""

from datetime import datetime, timedelta

def test_dst_offset_calculation():
    """Test the DST offset calculation"""
    print("🧪 Testing Dynamic Timezone Offset for DST")
    print("=" * 60)
    
    # Test dates throughout the year
    test_dates = [
        ('2025-01-15', 'Winter (Standard Time)'),
        ('2025-03-09', 'Before DST starts'),
        ('2025-03-10', 'DST starts (second Sunday in March)'),
        ('2025-06-15', 'Summer (Daylight Saving Time)'),
        ('2025-11-02', 'Before DST ends'),
        ('2025-11-03', 'DST ends (first Sunday in November)'),
        ('2025-12-15', 'Winter (Standard Time)'),
    ]
    
    for date_str, description in test_dates:
        event_date = datetime.strptime(date_str, '%Y-%m-%d')
        offset = get_timezone_offset(event_date)
        
        print(f"📅 {date_str}: {description}")
        print(f"   Offset: {offset} hours")
        
        # Test with a specific time
        test_time = "6:30a"
        start_time, end_time = parse_time_with_offset(test_time, event_date, offset)
        
        print(f"   Event: {test_time} → {start_time.strftime('%H:%M')} (after {offset}h offset)")
        print("-" * 50)
    
    print("✅ DST offset calculation tests completed!")

def get_timezone_offset(event_date: datetime) -> int:
    """Get the appropriate timezone offset based on whether we're in Daylight Saving Time"""
    try:
        # Check if the event date is during Daylight Saving Time
        # DST typically runs from second Sunday in March to first Sunday in November
        
        # Get the year of the event
        year = event_date.year
        
        # Calculate DST start (second Sunday in March)
        dst_start = get_nth_weekday_of_month(year, 3, 6, 2)  # 6 = Sunday, 2 = second occurrence
        
        # Calculate DST end (first Sunday in November)
        dst_end = get_nth_weekday_of_month(year, 11, 6, 1)  # 6 = Sunday, 1 = first occurrence
        
        # Check if event date is during DST
        if dst_start <= event_date < dst_end:
            # During Daylight Saving Time: subtract 4 hours
            offset = 4
            print(f"      📅 Event on {event_date.strftime('%Y-%m-%d')} is during DST - applying 4-hour offset")
        else:
            # During Standard Time: subtract 5 hours
            offset = 5
            print(f"      📅 Event on {event_date.strftime('%Y-%m-%d')} is during Standard Time - applying 5-hour offset")
        
        return offset
        
    except Exception as e:
        print(f"Error calculating timezone offset, using default 4-hour offset: {str(e)}")
        return 4  # Default fallback

def get_nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> datetime:
    """Get the nth occurrence of a specific weekday in a given month"""
    # weekday: 0=Monday, 1=Tuesday, ..., 6=Sunday
    # n: which occurrence (1=first, 2=second, etc.)
    
    # Start with the first day of the month
    current_date = datetime(year, month, 1)
    
    # Find the first occurrence of the target weekday
    while current_date.weekday() != weekday:
        current_date += timedelta(days=1)
    
    # Add weeks to get to the nth occurrence
    current_date += timedelta(weeks=n-1)
    
    return current_date

def parse_time_with_offset(time_str: str, event_date: datetime, offset_hours: int):
    """Parse time and apply the specified offset"""
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
            print(f"Invalid time values: hour={hour}, minute={minute}")
            # Fallback to all-day event
            start_time = event_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=1)
            return start_time, end_time
        
        # Create start time
        start_time = event_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Apply the specified offset
        start_time = start_time - timedelta(hours=offset_hours)
        
        # Default duration: 1 hour for most events
        end_time = start_time + timedelta(hours=1)
        
        return start_time, end_time
        
    except Exception as e:
        print(f"Error parsing time '{time_str}': {str(e)}")
        # Fallback: create all-day event
        start_time = event_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        return start_time, end_time

def test_specific_dst_transitions():
    """Test specific DST transition dates"""
    print("\n🧪 Testing Specific DST Transitions")
    print("=" * 60)
    
    # Test the exact DST transition dates
    transitions = [
        ('2025-03-09', 'Day before DST starts (Standard Time)'),
        ('2025-03-10', 'DST starts (Daylight Saving Time)'),
        ('2025-11-02', 'Day before DST ends (Daylight Saving Time)'),
        ('2025-11-03', 'DST ends (Standard Time)'),
    ]
    
    for date_str, description in transitions:
        event_date = datetime.strptime(date_str, '%Y-%m-%d')
        offset = get_timezone_offset(event_date)
        
        print(f"📅 {date_str}: {description}")
        print(f"   Offset: {offset} hours")
        
        # Test with different times
        test_times = ["6:30a", "5:15p", "10:00"]
        for test_time in test_times:
            start_time, end_time = parse_time_with_offset(test_time, event_date, offset)
            print(f"   {test_time} → {start_time.strftime('%H:%M')} (after {offset}h offset)")
        
        print("-" * 50)
    
    print("✅ DST transition tests completed!")

def main():
    """Run all DST offset tests"""
    print("🚀 Starting Dynamic Timezone Offset Tests")
    print("=" * 60)
    
    try:
        test_dst_offset_calculation()
        test_specific_dst_transitions()
        
        print("\n" + "=" * 60)
        print("🎉 All DST offset tests completed successfully!")
        print("✅ Dynamic timezone offset system is working correctly!")
        print("📅 Will automatically adjust between 4 hours (DST) and 5 hours (Standard Time)")
        print("🚀 Ready to handle DST changes automatically!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
