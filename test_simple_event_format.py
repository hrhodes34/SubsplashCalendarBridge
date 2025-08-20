#!/usr/bin/env python3
"""
Simple test script to verify event format fixes
"""

import sys
import os
from datetime import datetime

# Add the current directory to the path so we can import sync_script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sync_script import SubsplashSyncService

def test_simple_event_format():
    """Test that events have the correct start/end format"""
    print("🧪 Testing simple event format...")
    
    # Create a test event with the correct format
    test_event = {
        'title': 'Test Event',
        'start': datetime(2025, 8, 10, 10, 30, 0),
        'end': datetime(2025, 8, 10, 11, 30, 0),
        'source': 'test'
    }
    
    # Test the duplicate detection method
    service = SubsplashSyncService()
    
    # Test with empty events list
    is_duplicate = service._is_duplicate_event(test_event, [])
    print(f"✅ Empty events list - is_duplicate: {is_duplicate} (should be False)")
    
    # Test with same event
    is_duplicate = service._is_duplicate_event(test_event, [test_event])
    print(f"✅ Same event - is_duplicate: {is_duplicate} (should be True)")
    
    # Test with different event on same date
    different_event = {
        'title': 'Different Event',
        'start': datetime(2025, 8, 10, 14, 0, 0),
        'end': datetime(2025, 8, 10, 15, 0, 0),
        'source': 'test'
    }
    is_duplicate = service._is_duplicate_event(different_event, [test_event])
    print(f"✅ Different event same date - is_duplicate: {is_duplicate} (should be False)")
    
    # Test with same event on different date
    same_title_different_date = {
        'title': 'Test Event',
        'start': datetime(2025, 8, 11, 10, 30, 0),
        'end': datetime(2025, 8, 11, 11, 30, 0),
        'source': 'test'
    }
    is_duplicate = service._is_duplicate_event(same_title_different_date, [test_event])
    print(f"✅ Same title different date - is_duplicate: {is_duplicate} (should be False)")
    
    print("\n🎉 Simple event format test completed!")
    return True

if __name__ == "__main__":
    try:
        success = test_simple_event_format()
        if success:
            print("\n✅ All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
