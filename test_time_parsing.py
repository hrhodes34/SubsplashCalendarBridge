#!/usr/bin/env python3
"""
Test script for time parsing logic
"""

import sys
import os
from datetime import datetime, timedelta

# Add the current directory to the path so we can import sync_script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sync_script import SubsplashCalendarSync

def test_time_parsing():
    """Test the time parsing logic with various formats"""
    print("🧪 Testing time parsing logic...")
    
    # Create a sync instance to access the time parsing method
    sync = SubsplashCalendarSync()
    
    # Test cases based on the expected FullCalendar format
    test_cases = [
        ("6:30a", "2025-09-04"),  # Early Morning Prayer
        ("5:15p", "2025-09-02"),  # Prayer Set
        ("7:15a", "2025-09-01"),  # BAM
        ("10:00a", "2025-09-15"),
        ("2:30p", "2025-09-20"),
        ("12:00p", "2025-09-25"),  # Noon
        ("12:00a", "2025-09-30"),  # Midnight
    ]
    
    for time_str, date_str in test_cases:
        try:
            event_date = datetime.strptime(date_str, '%Y-%m-%d')
            start_time, end_time = sync._parse_fc_time(time_str, event_date)
            
            print(f"✅ Time: {time_str:>6} | Date: {date_str} | Start: {start_time.strftime('%Y-%m-%d %H:%M')} | End: {end_time.strftime('%Y-%m-%d %H:%M')} | All Day: {sync._is_all_day_event(start_time, end_time)}")
            
        except Exception as e:
            print(f"❌ Time: {time_str:>6} | Date: {date_str} | Error: {e}")
    
    print("\n🔍 Testing edge cases...")
    
    # Test edge cases
    edge_cases = [
        ("", "2025-09-01"),  # Empty time
        ("all day", "2025-09-01"),  # All day text
        ("invalid", "2025-09-01"),  # Invalid time
    ]
    
    for time_str, date_str in edge_cases:
        try:
            event_date = datetime.strptime(date_str, '%Y-%m-%d')
            start_time, end_time = sync._parse_fc_time(time_str, event_date)
            
            print(f"✅ Time: {time_str:>10} | Date: {date_str} | Start: {start_time.strftime('%Y-%m-%d %H:%M')} | End: {end_time.strftime('%Y-%m-%d %H:%M')} | All Day: {sync._is_all_day_event(start_time, end_time)}")
            
        except Exception as e:
            print(f"❌ Time: {time_str:>10} | Date: {date_str} | Error: {e}")

if __name__ == "__main__":
    test_time_parsing()
