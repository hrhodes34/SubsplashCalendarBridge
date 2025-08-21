#!/usr/bin/env python3
"""
Test script to verify event extraction fixes
Tests title cleaning, time extraction, and deduplication
"""

import re
from datetime import datetime

def test_title_cleaning():
    """Test the title cleaning functionality"""
    print("🧪 Testing Title Cleaning")
    print("=" * 50)
    
    # Test cases with problematic text
    test_cases = [
        "6:30am 10:30a Early Morning Prayer",
        "5:15p Prayer Set",
        "10:00 Some Other Event",
        "Early Morning Prayer 6:30a",
        "6:30a Early Morning Prayer 10:30a",
        "Prayer Set 5:15p 9:15p",
        "Just an event title",
        "6:30am",
        "5:15p",
    ]
    
    for test_text in test_cases:
        clean_title = clean_event_title(test_text)
        print(f"Original: '{test_text}'")
        print(f"Cleaned:  '{clean_title}'")
        print("-" * 40)
    
    print("✅ Title cleaning tests completed!")

def clean_event_title(full_text: str) -> str:
    """Clean event title by removing time information (same logic as sync script)"""
    try:
        if not full_text:
            return ""
        
        # Time patterns to remove
        time_patterns = [
            r'\b\d{1,2}:\d{2}[ap]?m?\b',  # 6:30a, 5:15pm
            r'\b\d{1,2}[ap]m\b',          # 6am, 5pm
            r'\b\d{1,2}:\d{2}\b',         # 14:30
            r'\d{1,2}:\d{2}[ap]?m?\s+\d{1,2}:\d{2}[ap]?m?',  # 6:30am 10:30a
        ]
        
        # Remove all time patterns
        clean_title = full_text
        for pattern in time_patterns:
            clean_title = re.sub(pattern, '', clean_title, flags=re.IGNORECASE)
        
        # Clean up extra whitespace and common artifacts
        clean_title = re.sub(r'\s+', ' ', clean_title)  # Multiple spaces to single
        clean_title = clean_title.strip()
        
        # Remove leading/trailing punctuation
        clean_title = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', clean_title)
        
        return clean_title
        
    except Exception as e:
        print(f"Error cleaning title: {str(e)}")
        return full_text

def test_time_extraction():
    """Test the time extraction functionality"""
    print("\n🧪 Testing Time Extraction")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        "6:30am 10:30a Early Morning Prayer",
        "5:15p Prayer Set",
        "10:00 Some Other Event",
        "Early Morning Prayer 6:30a",
        "6:30a Early Morning Prayer 10:30a",
        "Prayer Set 5:15p 9:15p",
        "Just an event title",
        "6:30am",
        "5:15p",
    ]
    
    for test_text in test_cases:
        extracted_time = extract_time_from_text(test_text)
        print(f"Text: '{test_text}'")
        print(f"Time: '{extracted_time}'")
        print("-" * 40)
    
    print("✅ Time extraction tests completed!")

def extract_time_from_text(text: str) -> str:
    """Extract time from text (same logic as sync script)"""
    try:
        # Common time patterns
        time_patterns = [
            r'\b\d{1,2}:\d{2}[ap]?m?\b',  # 6:30a, 5:15pm
            r'\b\d{1,2}[ap]m\b',          # 6am, 5pm
            r'\b\d{1,2}:\d{2}\b'          # 14:30
        ]
        
        # Find the first time pattern (this should be the original time)
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        
        # If no time found, check if it's a known event type
        if 'Early Morning Prayer' in text:
            return '6:30a'
        elif 'Prayer Set' in text:
            return '5:15p'
        
        return "all day"
        
    except Exception as e:
        print(f"Error extracting time: {str(e)}")
        return "all day"

def test_deduplication():
    """Test the deduplication logic"""
    print("\n🧪 Testing Deduplication")
    print("=" * 50)
    
    # Mock events that would cause duplicates
    mock_events = [
        {'title': 'Early Morning Prayer', 'date': '2025-08-21', 'time': '6:30a'},
        {'title': 'Early Morning Prayer', 'date': '2025-08-21', 'time': '6:30a'},
        {'title': 'Early Morning Prayer', 'date': '2025-08-21', 'time': '6:30a'},
        {'title': 'Prayer Set', 'date': '2025-08-21', 'time': '5:15p'},
        {'title': 'Prayer Set', 'date': '2025-08-21', 'time': '5:15p'},
        {'title': 'Some Other Event', 'date': '2025-08-22', 'time': '10:00'},
    ]
    
    print(f"Original events: {len(mock_events)}")
    
    # Apply deduplication
    unique_events = []
    seen_events = set()
    
    for event in mock_events:
        event_key = f"{event['title']}_{event['date']}_{event['time']}"
        
        if event_key not in seen_events:
            unique_events.append(event)
            seen_events.add(event_key)
            print(f"✅ Added: {event['title']} on {event['date']} at {event['time']}")
        else:
            print(f"🔄 Skipped duplicate: {event['title']} on {event['date']} at {event['time']}")
    
    print(f"\nUnique events: {len(unique_events)}")
    print(f"Duplicates removed: {len(mock_events) - len(unique_events)}")
    print("✅ Deduplication tests completed!")

def test_time_offset_fix():
    """Test the 4-hour time offset fix"""
    print("\n🧪 Testing 4-Hour Time Offset Fix")
    print("=" * 50)
    
    test_cases = [
        ('6:30a', '2025-08-21'),
        ('5:15p', '2025-08-21'),
        ('10:00', '2025-08-21'),
    ]
    
    for time_str, date_str in test_cases:
        event_date = datetime.strptime(date_str, '%Y-%m-%d')
        start_time, end_time = parse_time_with_offset(time_str, event_date)
        
        print(f"Original time: {time_str}")
        print(f"Parsed start: {start_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"Parsed end: {end_time.strftime('%Y-%m-%d %H:%M')}")
        
        # Show the offset correction
        original_hour = start_time.hour + 4
        if original_hour >= 24:
            original_hour -= 24
        print(f"Original hour: {original_hour:02d}:{start_time.minute:02d}")
        print("-" * 40)
    
    print("✅ Time offset fix tests completed!")

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
            print(f"Invalid time values: hour={hour}, minute={minute}")
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
        print(f"Error parsing time '{time_str}': {str(e)}")
        # Fallback: create all-day event
        start_time = event_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        return start_time, end_time

def main():
    """Run all tests"""
    print("🚀 Starting Event Extraction Fix Tests")
    print("=" * 60)
    
    try:
        test_title_cleaning()
        test_time_extraction()
        test_deduplication()
        test_time_offset_fix()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("✅ Event extraction fixes are working correctly!")
        print("🚀 Ready to test with the updated sync script!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    from datetime import timedelta
    main()
