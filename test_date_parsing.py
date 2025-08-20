#!/usr/bin/env python3
"""
Test script to verify date parsing logic
"""

from datetime import datetime
from dateutil import parser
import re

def test_date_parsing():
    """Test various date formats that might appear in Subsplash"""
    
    print("🧪 Testing Date Parsing Logic")
    print("=" * 50)
    
    # Test various date formats
    test_dates = [
        "August 1, 2024",
        "Aug 1, 2024", 
        "8/1/2024",
        "08/01/2024",
        "2024-08-01",
        "1 Aug 2024",
        "August 1st, 2024",
        "Aug 1st, 2024",
        "1st August 2024",
        "Today",
        "Tomorrow",
        "Next Monday",
        "Next Week",
        "This Weekend"
    ]
    
    for date_str in test_dates:
        try:
            # Try to parse the date
            parsed_date = parser.parse(date_str, fuzzy=True)
            print(f"✅ '{date_str}' → {parsed_date.strftime('%Y-%m-%d %H:%M')}")
        except Exception as e:
            print(f"❌ '{date_str}' → Error: {str(e)}")
    
    print("\n🔍 Testing Relative Date Logic")
    print("=" * 50)
    
    # Test relative date logic
    from datetime import datetime, timedelta
    
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    
    print(f"Today: {today.strftime('%Y-%m-%d')}")
    print(f"Tomorrow: {tomorrow.strftime('%Y-%m-%d')}")
    print(f"Next Week: {next_week.strftime('%Y-%m-%d')}")
    
    print("\n🔍 Testing Event Key Creation")
    print("=" * 50)
    
    # Test the event key creation logic from sync_script
    def create_test_event_key(title, start_date, is_all_day=False):
        """Test the event key creation logic"""
        try:
            title_clean = title.strip().lower()
            
            if is_all_day:
                date_str = start_date.date().isoformat()
                return f"{title_clean}_{date_str}_allday"
            else:
                # Round to nearest 5 minutes
                timestamp = start_date.timestamp()
                rounded_timestamp = round(timestamp / 300) * 300
                rounded_dt = datetime.fromtimestamp(rounded_timestamp)
                return f"{title_clean}_{rounded_dt.strftime('%Y%m%d_%H%M')}"
                
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    # Test with sample events
    test_events = [
        ("BAM!", datetime(2024, 8, 1, 19, 0), False),
        ("Kingdom Kids Camp", datetime(2024, 8, 24, 10, 30), False),
        ("Prayer Set", datetime(2024, 8, 26, 0, 0), True),
        ("Youth Retreat", datetime(2024, 8, 22, 18, 0), False)
    ]
    
    for title, start_date, is_all_day in test_events:
        key = create_test_event_key(title, start_date, is_all_day)
        print(f"📅 '{title}' on {start_date.strftime('%Y-%m-%d %H:%M')} → {key}")

if __name__ == "__main__":
    test_date_parsing()
