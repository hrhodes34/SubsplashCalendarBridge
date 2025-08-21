#!/usr/bin/env python3
"""
Test calendar navigation to see if we can get to September
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_calendar_navigation():
    """Test navigating to September in the calendar"""
    print("🔍 Testing calendar navigation...")
    
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
        
        print(f"📄 Initial page title: {browser.title}")
        
        # Check initial month
        try:
            toolbar = browser.find_element(By.CSS_SELECTOR, '.fc-toolbar-title')
            initial_month = toolbar.text.strip()
            print(f"📅 Initial month: {initial_month}")
        except Exception as e:
            print(f"❌ Error getting initial month: {e}")
            return
        
        # Navigate to next month (September)
        print("\n➡️ Navigating to next month...")
        try:
            next_button = browser.find_element(By.CSS_SELECTOR, '.fc-next-button')
            next_button.click()
            
            # Wait for calendar to update
            time.sleep(3)
            
            # Check new month
            toolbar = browser.find_element(By.CSS_SELECTOR, '.fc-toolbar-title')
            new_month = toolbar.text.strip()
            print(f"📅 New month: {new_month}")
            
            if "September" in new_month:
                print("✅ Successfully navigated to September!")
                
                # Now test finding events in September
                print("\n🎯 Testing event extraction in September...")
                
                # Find day cells
                day_cells = browser.find_elements(By.CSS_SELECTOR, 'td.fc-daygrid-day')
                print(f"Found {len(day_cells)} day cells")
                
                # Check first few cells for data-date
                for i, cell in enumerate(day_cells[:10]):
                    try:
                        data_date = cell.get_attribute('data-date')
                        if data_date:
                            print(f"  Cell {i}: data-date='{data_date}'")
                    except Exception as e:
                        continue
                
                # Find events
                events = browser.find_elements(By.CSS_SELECTOR, 'a.fc-event')
                print(f"\nFound {len(events)} events in September")
                
                # Check events
                for i, event in enumerate(events[:5]):
                    try:
                        # Get time
                        time_elem = event.find_element(By.CSS_SELECTOR, '.fc-event-time')
                        time_text = time_elem.text.strip() if time_elem else "NO_TIME"
                        
                        # Get title
                        title_elem = event.find_element(By.CSS_SELECTOR, '.fc-event-title')
                        title_text = title_elem.text.strip() if title_elem else "NO_TITLE"
                        
                        print(f"  Event {i}: time='{time_text}' title='{title_text}'")
                        
                        # Test finding parent day cell
                        try:
                            parent_cell = event.find_element(By.XPATH, './ancestor::td[contains(@class, "fc-daygrid-day")]')
                            if parent_cell:
                                cell_date = parent_cell.get_attribute('data-date')
                                print(f"    Parent cell date: {cell_date}")
                            else:
                                print(f"    No parent cell found")
                        except Exception as e:
                            print(f"    Error finding parent cell: {e}")
                            
                    except Exception as e:
                        print(f"  Event {i}: Error getting event info: {e}")
                
            else:
                print(f"❌ Still not in September: {new_month}")
                
        except Exception as e:
            print(f"❌ Error navigating to next month: {e}")
        
        browser.quit()
        print("\n✅ Browser closed")
        
    except Exception as e:
        print(f"❌ Browser setup failed: {e}")

if __name__ == "__main__":
    test_calendar_navigation()
