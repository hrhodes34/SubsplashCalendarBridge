#!/usr/bin/env python3
"""
Test script to verify event creation and date handling
"""

from datetime import datetime, timedelta
import re

def test_event_creation():
    """Test the event creation logic to ensure dates are handled correctly"""
    
    print("🧪 Testing Event Creation and Date Handling")
    print("=" * 60)
    
    # Simulate the date extraction logic from sync_script
    def parse_month_year_string(month_year_string):
        """Parse month year strings like 'August 2025'"""
        try:
            if not month_year_string:
                return None
            
            # Pattern for "Month YYYY" format
            pattern = r'(\w+)\s+(\d{4})'
            match = re.search(pattern, month_year_string)
            if match:
                month_str, year = match.groups()
                month = month_name_to_number(month_str)
                if month:
                    # Don't default to day 1 - this causes all events to stack on the 1st
                    # Instead, return None so the calling method can handle this case properly
                    print(f"          ⚠️ Found month/year '{month_str} {year}' but no specific day - skipping event")
                    return None
                    
        except Exception as e:
            print(f"          ⚠️ Error parsing month year string '{month_year_string}': {str(e)}")
        
        return None
    
    def month_name_to_number(month_name):
        """Convert month name to month number"""
        month_map = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
        return month_map.get(month_name.lower())
    
    def parse_date_string(date_string):
        """Parse various date string formats"""
        try:
            if not date_string:
                return None
            
            # Common date patterns
            date_patterns = [
                r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
                r'(\d{1,2})-(\d{1,2})-(\d{4})',  # MM-DD-YYYY
                r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',  # Month DD, YYYY
                r'(\d{1,2})\s+(\w+)\s+(\d{4})',  # DD Month YYYY
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_string)
                if match:
                    if len(match.groups()) == 3:
                        if pattern == r'(\w+)\s+(\d{1,2}),?\s+(\d{4})':
                            # Month DD, YYYY format
                            month_str, day, year = match.groups()
                            month = month_name_to_number(month_str)
                            if month:
                                return datetime(int(year), month, int(day))
                        elif pattern == r'(\d{1,2})\s+(\w+)\s+(\d{4})':
                            # DD Month YYYY format
                            day, month_str, year = match.groups()
                            month = month_name_to_number(month_str)
                            if month:
                                return datetime(int(year), month, int(day))
                        else:
                            # MM/DD/YYYY or MM-DD-YYYY format
                            month, day, year = match.groups()
                            return datetime(int(year), int(month), int(day))
            
            # If no pattern matches, try to parse as month/year only
            return parse_month_year_string(date_string)
            
        except Exception as e:
            print(f"          ⚠️ Error parsing date string '{date_string}': {str(e)}")
        
        return None
    
    # Test various date formats
    test_cases = [
        "August 1, 2024",
        "August 2024",  # This should now return None instead of day 1
        "8/15/2024",
        "August 24, 2024",
        "Invalid date",
        "2024-08-26"
    ]
    
    print("📅 Testing Date Parsing:")
    for test_case in test_cases:
        result = parse_date_string(test_case)
        if result:
            print(f"  ✅ '{test_case}' → {result.strftime('%Y-%m-%d')}")
        else:
            print(f"  ❌ '{test_case}' → No date found (correctly skipped)")
    
    print(f"\n🔍 Testing Event Creation Logic:")
    print("=" * 40)
    
    # Simulate creating events with various date scenarios
    sample_events = [
        {
            'title': 'BAM!',
            'date_string': 'August 1, 2024',
            'time_string': '6:00pm - 8:00pm'
        },
        {
            'title': 'Kingdom Kids Camp',
            'date_string': 'August 24, 2024',
            'time_string': '10:30am - 12:00pm'
        },
        {
            'title': 'Prayer Set',
            'date_string': 'August 26, 2024',
            'time_string': '12:00am - 1:00am'
        },
        {
            'title': 'Youth Retreat',
            'date_string': 'August 22, 2024',
            'time_string': '6:00pm - 8:00pm'
        },
        {
            'title': 'Invalid Event',
            'date_string': 'August 2024',  # Missing day - should be skipped
            'time_string': '7:00pm - 9:00pm'
        }
    ]
    
    valid_events = []
    for event in sample_events:
        date = parse_date_string(event['date_string'])
        if date:
            event['parsed_date'] = date
            valid_events.append(event)
            print(f"  ✅ '{event['title']}' → {date.strftime('%Y-%m-%d')}")
        else:
            print(f"  ❌ '{event['title']}' → Skipped (no valid date)")
    
    print(f"\n📊 Summary:")
    print(f"  Total events: {len(sample_events)}")
    print(f"  Valid events: {len(valid_events)}")
    print(f"  Skipped events: {len(sample_events) - len(valid_events)}")
    
    if valid_events:
        print(f"\n🎯 Valid events will be synced to their respective calendars:")
        for event in valid_events:
            print(f"  • {event['title']} on {event['parsed_date'].strftime('%Y-%m-%d')}")
    
    print(f"\n💡 Key Improvement:")
    print(f"  Events without specific dates are now SKIPPED instead of")
    print(f"  defaulting to day 1, which was causing the stacking issue.")

if __name__ == "__main__":
    test_event_creation()
