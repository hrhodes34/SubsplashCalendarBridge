#!/usr/bin/env python3
"""
Test Selenium selectors to debug why event extraction is failing
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_selenium_selectors():
    """Test the Selenium selectors that should work"""
    print("🔍 Testing Selenium selectors...")
    
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
        
        # Test 1: Find day cells
        print("\n📅 Test 1: Finding day cells with Selenium...")
        try:
            day_cells = browser.find_elements(By.CSS_SELECTOR, 'td.fc-daygrid-day')
            print(f"Found {len(day_cells)} day cells with 'td.fc-daygrid-day'")
            
            # Check first few cells
            for i, cell in enumerate(day_cells[:5]):
                try:
                    data_date = cell.get_attribute('data-date')
                    print(f"  Cell {i}: data-date='{data_date}'")
                except Exception as e:
                    print(f"  Cell {i}: Error getting data-date: {e}")
        except Exception as e:
            print(f"❌ Error finding day cells: {e}")
        
        # Test 2: Find events
        print("\n🎯 Test 2: Finding events with Selenium...")
        try:
            events = browser.find_elements(By.CSS_SELECTOR, 'a.fc-event')
            print(f"Found {len(events)} events with 'a.fc-event'")
            
            # Check first few events
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
        except Exception as e:
            print(f"❌ Error finding events: {e}")
        
        # Test 3: Alternative selectors
        print("\n🔍 Test 3: Trying alternative selectors...")
        selectors_to_try = [
            'a.fc-event',
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
        
        # Test 4: Check if calendar is loaded
        print("\n📊 Test 4: Checking calendar state...")
        try:
            # Check for calendar container
            calendar_container = browser.find_elements(By.CSS_SELECTOR, '.fc-view-container')
            print(f"Calendar containers found: {len(calendar_container)}")
            
            # Check for toolbar
            toolbar = browser.find_elements(By.CSS_SELECTOR, '.fc-toolbar-title')
            if toolbar:
                print(f"Toolbar title: {toolbar[0].text}")
            
            # Check for any FullCalendar elements
            fc_elements = browser.find_elements(By.CSS_SELECTOR, '[class*="fc-"]')
            print(f"Elements with fc- classes: {len(fc_elements)}")
            
        except Exception as e:
            print(f"Error checking calendar state: {e}")
        
        browser.quit()
        print("\n✅ Browser closed")
        
    except Exception as e:
        print(f"❌ Browser setup failed: {e}")

if __name__ == "__main__":
    test_selenium_selectors()
