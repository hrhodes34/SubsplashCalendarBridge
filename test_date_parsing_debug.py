#!/usr/bin/env python3
"""
Debug script to show exactly what text is being parsed for dates
"""

import re
from datetime import datetime
from dateutil import parser

def test_date_parsing():
    """Test the date parsing with the problematic text from your logs"""
    
    # This is the actual text being parsed (from your error logs)
    problematic_texts = [
        "at 10:30 AMLifegroups throughout the weekSUNDAY MORNINGS:Blowing Rock School165 Morris St.",
        "NC 28605ContactMailing Address:P.O.",
        "NC 28607",
        "Suite 12", 
        "NC 28607Follow Uspowered by SnapPages"
    ]
    
    print("🔍 DEBUGGING DATE PARSING ISSUES")
    print("=" * 80)
    print("These are the actual text strings being parsed by your system:")
    print()
    
    for i, text in enumerate(problematic_texts, 1):
        print(f"📝 Text {i}: '{text}'")
        print(f"   Length: {len(text)} characters")
        print(f"   Contains date keywords: {'date' in text.lower() or 'time' in text.lower()}")
        print(f"   Contains month names: {any(month in text.lower() for month in ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'])}")
        time_pattern_found = bool(re.search(r'\d{1,2}:\d{2}[ap]m', text.lower()))
        print(f"   Contains time patterns: {time_pattern_found}")
        date_pattern_found = bool(re.search(r'[A-Za-z]+ \d{1,2},? \d{4}', text))
        print(f"   Contains date patterns: {date_pattern_found}")
        print()
    
    print("=" * 80)
    print("💡 ANALYSIS:")
    print("   • None of these texts contain actual event dates")
    print("   • They are navigation text, contact info, and addresses")
    print("   • Your system is parsing the wrong content")
    print()
    print("🔧 SOLUTION:")
    print("   • Fix the event extraction to find actual calendar events")
    print("   • Don't parse random page text as events")
    print("   • Find the correct Subsplash calendar URLs or API endpoints")
    print()
    
    # Test what happens when we try to parse these
    print("🧪 TESTING PARSING ATTEMPTS:")
    print("-" * 40)
    
    for text in problematic_texts:
        result = parse_subsplash_datetime_debug(text)
        if result:
            print(f"✅ SUCCESS: '{text}' → {result}")
        else:
            print(f"❌ FAILED: '{text}' → No valid date found")
        print()

def parse_subsplash_datetime_debug(date_time_text):
    """Debug version of the date parsing method"""
    try:
        # Clean up the text
        date_time_text = date_time_text.strip()
        
        # Try single-day format: "August 20, 2025 from 6:00 - 8:00pm EDT"
        single_day_pattern = r'([A-Za-z]+ \d{1,2},? \d{4}) from (\d{1,2}:\d{2})([ap]m) - (\d{1,2}:\d{2})([ap]m)'
        single_match = re.search(single_day_pattern, date_time_text)
        
        if single_match:
            return f"Single day event: {single_match.group(1)}"
        
        # Try multi-day format
        multi_day_pattern = r'([A-Za-z]+ \d{1,2}),? (\d{1,2}:\d{2})([ap]m) - ([A-Za-z]+ \d{1,2},? \d{4}) (\d{1,2}:\d{2})([ap]m)'
        multi_match = re.search(multi_day_pattern, date_time_text)
        
        if multi_match:
            return f"Multi-day event: {multi_match.group(1)} to {multi_match.group(4)}"
        
        # Try simple date format: "August 20, 2025" (all day event)
        simple_date_pattern = r'([A-Za-z]+ \d{1,2},? \d{4})'
        simple_date_match = re.search(simple_date_pattern, date_time_text)
        
        if simple_date_match:
            return f"All-day event: {simple_date_match.group(1)}"
        
        # Try to extract any date and time patterns
        date_pattern = r'([A-Za-z]+ \d{1,2},? \d{4})'
        time_pattern = r'(\d{1,2}:\d{2})([ap]m)'
        
        date_match = re.search(date_pattern, date_time_text)
        time_matches = re.findall(time_pattern, date_time_text)
        
        if date_match and len(time_matches) >= 2:
            return f"Date with times: {date_match.group(1)}"
        
        return None
        
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    test_date_parsing()
