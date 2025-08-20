#!/usr/bin/env python3
"""
Debug script to examine the HTML structure of the calendar
to understand how to extract the specific day information for each event.
"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def debug_calendar_structure():
    """Debug the calendar structure to understand day extraction"""
    print("🔍 Debugging calendar structure...")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Initialize driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Navigate to the calendar
        print("🌐 Navigating to antiochboone.com/calendar...")
        driver.get("https://antiochboone.com/calendar")
        time.sleep(3)
        
        # Wait for calendar to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".fc-calendar"))
        )
        
        print("✅ Calendar loaded")
        
        # Get the current month/year
        try:
            month_year = driver.find_element(By.CSS_SELECTOR, ".fc-toolbar-title").text.strip()
            print(f"📅 Current month/year: {month_year}")
        except:
            print("❌ Could not get month/year")
        
        # Find all calendar day elements
        calendar_days = driver.find_elements(By.CSS_SELECTOR, ".fc-day")
        print(f"📅 Found {len(calendar_days)} calendar day elements")
        
        # Examine a few calendar days in detail
        for i, day in enumerate(calendar_days[:5]):
            print(f"\n--- Calendar Day {i+1} ---")
            
            # Get attributes
            classes = day.get_attribute("class")
            data_date = day.get_attribute("data-date")
            aria_label = day.get_attribute("aria-label")
            
            print(f"  Classes: {classes}")
            print(f"  data-date: {data_date}")
            print(f"  aria-label: {aria_label}")
            
            # Get text content
            day_text = day.text.strip()
            print(f"  Text content: {day_text}")
            
            # Look for events in this day
            events = day.find_elements(By.CSS_SELECTOR, ".fc-event")
            print(f"  Events found: {len(events)}")
            
            for j, event in enumerate(events[:2]):  # Show first 2 events
                print(f"    Event {j+1}:")
                event_text = event.text.strip()
                print(f"      Text: {event_text}")
                
                # Get event attributes
                event_classes = event.get_attribute("class")
                event_title = event.get_attribute("title")
                print(f"      Classes: {event_classes}")
                print(f"      Title: {event_title}")
                
                # Look for parent elements to understand structure
                parent = event.find_element(By.XPATH, "..")
                parent_classes = parent.get_attribute("class")
                print(f"      Parent classes: {parent_classes}")
        
        # Look for specific date patterns in the HTML
        print("\n🔍 Looking for date patterns in HTML...")
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Look for data-date attributes
        data_dates = soup.find_all(attrs={"data-date": True})
        print(f"  Elements with data-date: {len(data_dates)}")
        for i, elem in enumerate(data_dates[:5]):
            data_date = elem.get("data-date")
            classes = elem.get("class", [])
            print(f"    {i+1}. data-date='{data_date}' classes={classes}")
        
        # Look for aria-label with dates
        aria_labels = soup.find_all(attrs={"aria-label": True})
        date_aria_labels = [elem for elem in aria_labels if any(char.isdigit() for char in elem.get("aria-label", ""))]
        print(f"  Elements with date-like aria-label: {len(date_aria_labels)}")
        for i, elem in enumerate(date_aria_labels[:5]):
            aria_label = elem.get("aria-label")
            classes = elem.get("class", [])
            print(f"    {i+1}. aria-label='{aria_label}' classes={classes}")
        
        # Save HTML for manual inspection
        with open("debug_calendar.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        print("\n💾 Saved HTML to debug_calendar.html for manual inspection")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()

if __name__ == "__main__":
    try:
        debug_calendar_structure()
        print("\n🎉 Debug completed!")
    except Exception as e:
        print(f"\n💥 Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
