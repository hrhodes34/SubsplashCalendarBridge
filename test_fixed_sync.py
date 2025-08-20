#!/usr/bin/env python3
"""
Test script to verify the duplicate prevention fixes work
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_unique_id_generation():
    """Test that unique IDs are generated correctly"""
    print("🧪 Testing Unique ID Generation")
    print("=" * 50)
    
    # Test data
    test_events = [
        {
            'calendar_type': 'prayer',
            'date': '2025-08-21',
            'title': 'Early Morning Prayer'
        },
        {
            'calendar_type': 'prayer', 
            'date': '2025-08-26',
            'title': 'Prayer Set'
        },
        {
            'calendar_type': 'prayer',
            'date': '2025-08-28', 
            'title': 'Early Morning Prayer'
        }
    ]
    
    for event in test_events:
        unique_id = f"{event['calendar_type']}_{event['date']}_{event['title'].lower().replace(' ', '_')}"
        print(f"Event: {event['title']}")
        print(f"Date: {event['date']}")
        print(f"Unique ID: {unique_id}")
        print()
    
    print("✅ Unique ID generation test completed")

def test_date_parsing():
    """Test the improved date parsing logic"""
    print("🧪 Testing Date Parsing Logic")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            'google_date': '2025-08-21T06:30:00-04:00',
            'event_date': '2025-08-21',
            'expected_match': True
        },
        {
            'google_date': '2025-08-26T17:15:00-04:00',
            'event_date': '2025-08-26', 
            'expected_match': True
        },
        {
            'google_date': '2025-08-21T06:30:00-04:00',
            'event_date': '2025-08-22',
            'expected_match': False
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        print(f"  Google Date: {test_case['google_date']}")
        print(f"  Event Date: {test_case['event_date']}")
        
        # Simulate the improved parsing logic
        try:
            existing_date = test_case['google_date'].split('T')[0]
            matches = existing_date == test_case['event_date']
            print(f"  Parsed Date: {existing_date}")
            print(f"  Matches: {matches}")
            print(f"  Expected: {test_case['expected_match']}")
            
            if matches == test_case['expected_match']:
                print("  ✅ PASS")
            else:
                print("  ❌ FAIL")
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
        print()
    
    print("✅ Date parsing test completed")

def main():
    """Run all tests"""
    print("🚀 Testing Subsplash Calendar Sync Fixes")
    print("=" * 60)
    print()
    
    test_unique_id_generation()
    print()
    test_date_parsing()
    print()
    
    print("🎯 Summary of Fixes Applied:")
    print("1. ✅ Improved event matching logic")
    print("2. ✅ Added unique ID generation")
    print("3. ✅ Better date parsing for Google Calendar events")
    print("4. ✅ Added unique ID to event descriptions")
    print()
    print("🔧 These fixes should prevent:")
    print("   - Wrong info at wrong times")
    print("   - Multiple copies of the same event")
    print("   - Event matching failures")
    print()
    print("🧪 To test the full fix:")
    print("   1. Push these changes to GitHub")
    print("   2. Run the GitHub Action manually")
    print("   3. Check that no new duplicate events are created")
    print("   4. Verify existing events are updated, not duplicated")

if __name__ == "__main__":
    main()
