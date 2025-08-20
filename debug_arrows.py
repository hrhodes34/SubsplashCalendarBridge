#!/usr/bin/env python3
"""
Debug script to find the actual navigation arrows on the calendar page
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def debug_calendar_navigation():
    """Debug the calendar page to find navigation arrows"""
    print("🔍 Debugging Calendar Navigation Arrows")
    print("=" * 50)
    
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize the driver
        print("🌐 Starting Chrome browser...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navigate to the calendar
        print("📅 Navigating to antiochboone.com/calendar...")
        driver.get("https://antiochboone.com/calendar")
        time.sleep(3)  # Wait for page to load
        
        # Get the page source to examine structure
        print("🔍 Examining page structure...")
        page_source = driver.page_source
        
        # Look for navigation elements
        print("\n🎯 Looking for navigation elements...")
        
        # Try to find any buttons or elements that might be navigation
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(all_buttons)} buttons on the page")
        
        for i, button in enumerate(all_buttons[:10]):  # Show first 10
            try:
                text = button.text.strip()
                aria_label = button.get_attribute("aria-label") or ""
                title = button.get_attribute("title") or ""
                class_name = button.get_attribute("class") or ""
                
                print(f"  Button {i+1}:")
                print(f"    Text: '{text}'")
                print(f"    Aria-label: '{aria_label}'")
                print(f"    Title: '{title}'")
                print(f"    Class: '{class_name}'")
                print()
            except Exception as e:
                print(f"  Button {i+1}: Error getting attributes - {e}")
        
        # Look for navigation arrows specifically
        print("🔍 Looking for navigation arrows...")
        
        # Common patterns for next/previous month
        arrow_patterns = [
            ">", "<", "→", "←", "next", "previous", "forward", "back",
            "chevron", "arrow", "nav", "month"
        ]
        
        for pattern in arrow_patterns:
            try:
                elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{pattern}')]")
                if elements:
                    print(f"  Found {len(elements)} elements containing '{pattern}':")
                    for elem in elements[:3]:  # Show first 3
                        tag = elem.tag_name
                        text = elem.text.strip()
                        class_name = elem.get_attribute("class") or ""
                        print(f"    <{tag}> '{text}' (class: {class_name})")
                    print()
            except Exception as e:
                continue
        
        # Look for calendar navigation structure
        print("📅 Looking for calendar navigation structure...")
        
        # Common calendar navigation selectors
        nav_selectors = [
            "[class*='calendar']",
            "[class*='nav']", 
            "[class*='month']",
            "[class*='header']",
            "[class*='controls']"
        ]
        
        for selector in nav_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"  Found {len(elements)} elements with selector '{selector}':")
                    for elem in elements[:3]:
                        tag = elem.tag_name
                        text = elem.text.strip()[:100]  # First 100 chars
                        class_name = elem.get_attribute("class") or ""
                        print(f"    <{tag}> '{text}' (class: {class_name})")
                    print()
            except Exception as e:
                continue
        
        # Save the page source for manual inspection
        print("💾 Saving page source for manual inspection...")
        with open("calendar_page_source.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        print("✅ Page source saved to calendar_page_source.html")
        
        driver.quit()
        print("\n🎯 Debug complete! Check calendar_page_source.html for the full HTML structure")
        
    except Exception as e:
        print(f"❌ Error during debug: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_calendar_navigation()
