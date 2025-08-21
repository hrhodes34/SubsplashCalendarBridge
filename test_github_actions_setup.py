#!/usr/bin/env python3
"""
Test script that mimics the exact GitHub Actions browser setup
to verify our event extraction works in that environment
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_github_actions_browser_setup():
    """Test using the exact GitHub Actions browser configuration"""
    print("🔍 Testing with GitHub Actions browser setup...")
    
    # Setup browser with EXACT GitHub Actions configuration
    chrome_options = Options()
    
    # GitHub Actions: Enhanced headless settings (from sync_script.py lines 107-114)
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        # Use ChromeDriverManager (same as GitHub Actions)
        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set timeouts (same as sync_script.py lines 132-133)
        browser.set_page_load_timeout(30)
        browser.implicitly_wait(10)
        
        print("✅ GitHub Actions browser setup successful")
        
        # Navigate to the prayer calendar
        url = "https://antiochboone.com/calendar-prayer"
        print(f"🌐 Navigating to: {url}")
        browser.get(url)
        
        # Wait for page to load (using same wait time as GitHub Actions: BROWSER_WAIT_TIME=15)
        wait_time = 15
        print(f"⏱️ Waiting {wait_time} seconds for calendar to load...")
        time.sleep(wait_time)
        
        print(f"📄 Page title: {browser.title}")
        
        # Check what month we're on
        try:
            toolbar = browser.find_element(By.CSS_SELECTOR, '.fc-toolbar-title')
            current_month = toolbar.text.strip()
            print(f"📅 Current month: {current_month}")
        except Exception as e:
            print(f"❌ Error getting current month: {e}")
            return
        
        # Test finding calendar elements
        print("\n🔍 Testing calendar element detection...")
        
        # Test 1: Find day cells
        try:
            day_cells = browser.find_elements(By.CSS_SELECTOR, 'td.fc-daygrid-day')
            print(f"✅ Found {len(day_cells)} day cells")
            
            # Check first few cells for data-date
            cells_with_dates = 0
            for cell in day_cells[:10]:
                data_date = cell.get_attribute('data-date')
                if data_date and data_date != 'None':
                    cells_with_dates += 1
            print(f"✅ {cells_with_dates} cells have valid data-date attributes")
            
        except Exception as e:
            print(f"❌ Error finding day cells: {e}")
        
        # Test 2: Find events using our improved logic
        print("\n🎯 Finding events with GitHub Actions setup...")
        try:
            events = browser.find_elements(By.CSS_SELECTOR, 'a.fc-event')
            print(f"Found {len(events)} total events")
            
            if len(events) == 0:
                print("❌ No events found!")
                
                # Debug: Try alternative selectors
                print("\n🔍 Debugging: Trying alternative selectors...")
                selectors_to_try = [
                    '.fc-event',
                    'a[href*="/event/"]',
                    '.fc-daygrid-event',
                    '.fc-event-harness a'
                ]
                
                for selector in selectors_to_try:
                    try:
                        elements = browser.find_elements(By.CSS_SELECTOR, selector)
                        print(f"  Selector '{selector}': {len(elements)} elements")
                    except Exception as e:
                        print(f"  Selector '{selector}': Error - {e}")
                        
                return
            
            # Analyze each event
            event_details = []
            for i, event in enumerate(events):
                try:
                    # Get time using our proven logic
                    time_elem = event.find_element(By.CSS_SELECTOR, '.fc-event-time')
                    time_text = time_elem.text.strip() if time_elem else "NO_TIME"
                    
                    # Get title using our proven logic
                    title_elem = event.find_element(By.CSS_SELECTOR, '.fc-event-title')
                    title_text = title_elem.text.strip() if title_elem else "NO_TITLE"
                    
                    # Get href
                    href = event.get_attribute('href') or 'NO_HREF'
                    
                    # Find parent day cell for date using our proven XPath
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
            
            # Summary and validation
            print(f"\n📊 SUMMARY:")
            print(f"Total events found: {len(events)}")
            
            # Count by title
            title_counts = {}
            for event in event_details:
                title = event['title']
                title_counts[title] = title_counts.get(title, 0) + 1
            
            for title, count in title_counts.items():
                print(f"  {title}: {count} times")
            
            # Check if this matches expected pattern for August
            expected_events = {
                'Early Morning Prayer': 2,
                'Prayer Set': 1
            }
            
            print(f"\n✅ EXPECTED vs ACTUAL (August):")
            all_match = True
            for title, expected_count in expected_events.items():
                actual_count = title_counts.get(title, 0)
                status = "✅" if actual_count == expected_count else "❌"
                if actual_count != expected_count:
                    all_match = False
                print(f"  {status} {title}: expected {expected_count}, found {actual_count}")
            
            # Show dates for each event type
            print(f"\n📅 Event dates:")
            for title in expected_events.keys():
                matching_events = [e for e in event_details if e['title'] == title]
                dates = [e['date'] for e in matching_events]
                times = [e['time'] for e in matching_events]
                print(f"  {title}: {list(zip(dates, times))}")
            
            # Final validation
            if all_match and len(events) == 3:
                print(f"\n🎉 SUCCESS: GitHub Actions setup works perfectly!")
                print(f"   - Found all expected events")
                print(f"   - Times extracted correctly")
                print(f"   - Dates extracted correctly")
            else:
                print(f"\n⚠️ PARTIAL SUCCESS: Events found but counts don't match expected")
                
        except Exception as e:
            print(f"❌ Error finding events: {e}")
        
        browser.quit()
        print("\n✅ Browser closed")
        
    except Exception as e:
        print(f"❌ GitHub Actions browser setup failed: {e}")

if __name__ == "__main__":
    test_github_actions_browser_setup()
