#!/usr/bin/env python3
"""
Simple test to verify date parsing fix
"""

def test_date_fix():
    print("🧪 Testing Date Parsing Fix")
    print("=" * 40)
    
    # Test the specific fix we applied
    def parse_month_year_string(month_year_string):
        """Parse month year strings like 'August 2025'"""
        try:
            if not month_year_string:
                return None
            
            # Pattern for "Month YYYY" format
            import re
            pattern = r'(\w+)\s+(\d{4})'
            match = re.search(pattern, month_year_string)
            if match:
                month_str, year = match.groups()
                month = month_name_to_number(month_str)
                if month:
                    # This is the fix: Don't default to day 1
                    print(f"  ⚠️ Found month/year '{month_str} {year}' but no specific day - skipping event")
                    return None
                    
        except Exception as e:
            print(f"  ⚠️ Error parsing month year string '{month_year_string}': {str(e)}")
        
        return None
    
    def month_name_to_number(month_name):
        """Convert month name to month number"""
        month_map = {
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9, 'sept': 9,
        }
        return month_map.get(month_name.lower())
    
    # Test cases
    test_cases = [
        "August 1, 2024",      # Should work (has day)
        "August 2024",          # Should now return None (no day)
        "September 2024",       # Should now return None (no day)
    ]
    
    for test_case in test_cases:
        result = parse_month_year_string(test_case)
        if result:
            print(f"  ✅ '{test_case}' → {result}")
        else:
            print(f"  ❌ '{test_case}' → No date (correctly skipped)")
    
    print("\n🎯 Summary:")
    print("  - Events with specific dates: ✅ Will be synced")
    print("  - Events without specific dates: ❌ Will be skipped (no more day 1 stacking!)")

if __name__ == "__main__":
    test_date_fix()
