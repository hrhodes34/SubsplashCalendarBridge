#!/usr/bin/env python3
"""
Simple test to check what events are found in August on the prayer calendar
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_august_events():
    """Test finding events in August on the prayer calendar"""
    print("🔍 Testing August events on prayer calendar...")
    
    # Setup browser
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    try:
        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service, options=chrome_options)
        browser.set_page_load_timeout(30)
        browser.implicitly_wait(10)
        
        print("✅ Browser setup successful")
        
        # Navigate to the prayer calendar
        url = "https://antiochboone.com/calendar-prayer"
        print(f"🌐 Navigating to: {url}")
        browser.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        print(f"📄 Page title: {browser.title}")
        
        # Check what month we're on
        try:
            toolbar = browser.find_element(By.CSS_SELECTOR, '.fc-toolbar-title')
            current_month = toolbar.text.strip()
            print(f"📅 Current month: {current_month}")
        except Exception as e:
            print(f"❌ Error getting current month: {e}")
            return
        
        # Find all events
        print("\n🎯 Finding all events...")
        try:
            events = browser.find_elements(By.CSS_SELECTOR, 'a.fc-event')
            print(f"Found {len(events)} total events")
            
            if len(events) == 0:
                print("❌ No events found!")
                return
            
            # Analyze each event
            event_details = []
            for i, event in enumerate(events):
                try:
                    # Get time
                    time_elem = event.find_element(By.CSS_SELECTOR, '.fc-event-time')
                    time_text = time_elem.text.strip() if time_elem else "NO_TIME"
                    
                    # Get title
                    title_elem = event.find_element(By.CSS_SELECTOR, '.fc-event-title')
                    title_text = title_elem.text.strip() if title_elem else "NO_TITLE"
                    
                    # Get href
                    href = event.get_attribute('href') or 'NO_HREF'
                    
                    # Find parent day cell for date
                    try:
                        parent_cell = event.find_element(By.XPATH, './ancestor::td[contains(@class, "fc-daygrid-day")]')
                        if parent_cell:
                            cell_date = parent_cell.get_attribute('data-date')
                        else:
                            cell_date = "NO_DATE"
                    except:
                        cell_date = "NO_DATE"
                    
                    event_details.append({
                        'index': i,
                        'time': time_text,
                        'title': title_text,
                        'href': href,
                        'date': cell_date
                    })
                    
                    print(f"  Event {i}: {time_text} - {title_text} on {cell_date}")
                    
                except Exception as e:
                    print(f"  Event {i}: Error getting event info: {e}")
            
            # Summary
            print(f"\n📊 SUMMARY:")
            print(f"Total events found: {len(events)}")
            
            # Count by title
            title_counts = {}
            for event in event_details:
                title = event['title']
                title_counts[title] = title_counts.get(title, 0) + 1
            
            for title, count in title_counts.items():
                print(f"  {title}: {count} times")
            
            # Check if this matches expected pattern
            expected_events = {
                'Early Morning Prayer': 2,
                'Prayer Set': 1
            }
            
            print(f"\n✅ EXPECTED vs ACTUAL:")
            for title, expected_count in expected_events.items():
                actual_count = title_counts.get(title, 0)
                status = "✅" if actual_count == expected_count else "❌"
                print(f"  {status} {title}: expected {expected_count}, found {actual_count}")
            
            # Show dates for each event type
            print(f"\n📅 Event dates:")
            for title in expected_events.keys():
                matching_events = [e for e in event_details if e['title'] == title]
                dates = [e['date'] for e in matching_events]
                print(f"  {title}: {dates}")
            
        except Exception as e:
            print(f"❌ Error finding events: {e}")
        
        browser.quit()
        print("\n✅ Browser closed")
        
    except Exception as e:
        print(f"❌ Browser setup failed: {e}")

if __name__ == "__main__":
    test_august_events()
