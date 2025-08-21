#!/usr/bin/env python3
"""
Test script to check for timezone offset issues
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_timezone_offset():
    """Test if there's a consistent timezone offset affecting event times"""
    print("🔍 Testing for timezone offset issues...")
    
    # Setup browser
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Navigate to prayer calendar
        url = "https://antiochboone.com/calendar-prayer"
        print(f"🌐 Navigating to: {url}")
        browser.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Find all events
        events = browser.find_elements(By.CSS_SELECTOR, 'a.fc-event')
        print(f"Found {len(events)} events")
        
        # Expected times vs. what we're getting
        expected_times = {
            'Early Morning Prayer': '6:30a',
            'Prayer Set': '5:15p',
            'BAM': '7:15a'
        }
        
        print("\n🔍 Analyzing event times...")
        print("=" * 60)
        
        for i, event in enumerate(events):
            try:
                # Get event title
                title_elem = event.find_element(By.CSS_SELECTOR, '.fc-event-title')
                title = title_elem.text.strip() if title_elem else "Unknown"
                
                # Get event time
                time_elem = event.find_element(By.CSS_SELECTOR, '.fc-event-time')
                actual_time = time_elem.text.strip() if time_elem else "No time"
                
                # Get event date
                day_cell = event.find_element(By.XPATH, './ancestor::td[contains(@class, "fc-daygrid-day")]')
                date_str = day_cell.get_attribute('data-date') if day_cell else "No date"
                
                print(f"Event {i+1}:")
                print(f"  Title: {title}")
                print(f"  Date: {date_str}")
                print(f"  Actual Time: {actual_time}")
                
                # Check if this matches an expected event
                if title in expected_times:
                    expected_time = expected_times[title]
                    print(f"  Expected Time: {expected_time}")
                    
                    # Calculate time difference
                    if actual_time and expected_time:
                        print(f"  ⚠️  TIME MISMATCH: Got {actual_time}, Expected {expected_time}")
                        
                        # Try to parse times to see the offset
                        try:
                            # Simple time parsing for comparison
                            actual_hour = int(actual_time.split(':')[0])
                            expected_hour = int(expected_time.split(':')[0])
                            
                            # Handle AM/PM
                            if 'p' in actual_time.lower() and actual_hour != 12:
                                actual_hour += 12
                            if 'p' in expected_time.lower() and expected_hour != 12:
                                expected_hour += 12
                            
                            hour_diff = actual_hour - expected_hour
                            print(f"  📊 Hour difference: {hour_diff} hours")
                            
                            if hour_diff != 0:
                                print(f"  🌍 Possible timezone offset: {hour_diff} hours")
                                
                        except:
                            print(f"  ❌ Could not parse time difference")
                    else:
                        print(f"  ✅ Time matches expected")
                else:
                    print(f"  ℹ️  Not a tracked event")
                
                print("-" * 40)
                
            except Exception as e:
                print(f"Event {i+1}: Error analyzing - {e}")
                print("-" * 40)
        
        # Check if there's a consistent pattern
        print("\n🔍 Checking for consistent timezone patterns...")
        
        # Look for any timezone indicators in the page
        page_source = browser.page_source.lower()
        timezone_indicators = ['utc', 'gmt', 'est', 'cst', 'mst', 'pst', 'edt', 'cdt', 'mdt', 'pdt']
        
        for tz in timezone_indicators:
            if tz in page_source:
                print(f"  Found timezone indicator: {tz.upper()}")
        
        # Check page title and any timezone info
        page_title = browser.title
        print(f"  Page title: {page_title}")
        
        # Look for any script tags with timezone info
        script_tags = browser.find_elements(By.TAG_NAME, 'script')
        for script in script_tags[:3]:  # Check first 3
            try:
                script_content = script.get_attribute('innerHTML')
                if script_content and any(tz in script_content.lower() for tz in timezone_indicators):
                    print(f"  Found timezone info in script: {script_content[:200]}...")
            except:
                continue
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    finally:
        browser.quit()

if __name__ == "__main__":
    test_timezone_offset()
