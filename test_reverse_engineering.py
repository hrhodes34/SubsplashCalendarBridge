#!/usr/bin/env python3
"""
Test script for the new reverse engineering methods
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_reverse_engineering_methods():
    """Test the new reverse engineering methods"""
    print("🔍 Testing reverse engineering methods...")
    
    # Setup browser with GitHub Actions configuration
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Setup service
    service = Service(ChromeDriverManager().install())
    
    # Create browser
    browser = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Navigate to prayer calendar
        url = "https://antiochboone.com/calendar-prayer"
        print(f"🌐 Navigating to: {url}")
        browser.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        print("🔍 Testing JavaScript extraction...")
        
        # Test JavaScript extraction
        js_script = """
        try {
            // Try to find FullCalendar instance
            var calendar = null;
            
            // Method 1: Look for global FullCalendar instance
            if (typeof window.FullCalendar !== 'undefined') {
                calendar = window.FullCalendar;
                console.log('Found global FullCalendar');
            }
            
            // Method 2: Look for jQuery FullCalendar
            if (!calendar && typeof $ !== 'undefined') {
                var fcElements = $('.fc');
                if (fcElements.length > 0) {
                    calendar = fcElements.fullCalendar('getCalendar');
                    console.log('Found jQuery FullCalendar');
                }
            }
            
            // Method 3: Look for vanilla JS FullCalendar
            if (!calendar) {
                var fcElements = document.querySelectorAll('.fc');
                for (var i = 0; i < fcElements.length; i++) {
                    if (fcElements[i].fullCalendar) {
                        calendar = fcElements[i].fullCalendar('getCalendar');
                        console.log('Found vanilla JS FullCalendar');
                        break;
                    }
                }
            }
            
            // Method 4: Look for any calendar-related objects
            if (!calendar) {
                console.log('Looking for calendar objects...');
                for (var key in window) {
                    try {
                        var obj = window[key];
                        if (obj && typeof obj === 'object' && obj.getEvents) {
                            console.log('Found potential calendar object:', key);
                            calendar = obj;
                            break;
                        }
                    } catch (e) {
                        // Skip if we can't access the property
                    }
                }
            }
            
            if (calendar && calendar.getEvents) {
                var allEvents = calendar.getEvents();
                console.log('Found events:', allEvents.length);
                
                var eventData = [];
                for (var i = 0; i < allEvents.length; i++) {
                    var event = allEvents[i];
                    eventData.push({
                        title: event.title || event.eventTitle,
                        start: event.start ? event.start.toISOString() : null,
                        end: event.end ? event.end.toISOString() : null,
                        allDay: event.allDay || false,
                        id: event.id || event.eventId,
                        url: event.url || null,
                        className: event.className || null
                    });
                }
                
                return { success: true, events: eventData, count: eventData.length };
            } else {
                console.log('No FullCalendar instance found');
                return { success: false, error: 'No FullCalendar instance found' };
            }
        } catch (e) {
            console.error('Error:', e);
            return { success: false, error: e.toString() };
        }
        """
        
        result = browser.execute_script(js_script)
        print(f"JavaScript result: {result}")
        
        if result and result.get('success') and result.get('events'):
            events = result['events']
            print(f"✅ Found {len(events)} events from JavaScript!")
            
            for i, event in enumerate(events[:5]):  # Show first 5
                print(f"  Event {i}: {event.get('title', 'Unknown')} at {event.get('start', 'No time')}")
        else:
            print(f"❌ JavaScript extraction failed: {result}")
        
        print("\n🔍 Testing network data extraction...")
        
        # Test network data extraction
        script_tags = browser.find_elements(By.TAG_NAME, 'script')
        print(f"Found {len(script_tags)} script tags")
        
        for i, script in enumerate(script_tags[:5]):  # Check first 5
            try:
                script_content = script.get_attribute('innerHTML')
                if script_content and ('events' in script_content.lower() or 'calendar' in script_content.lower()):
                    print(f"Script {i} contains potential event data: {script_content[:100]}...")
            except:
                continue
        
        print("\n🔍 Testing alternative selectors...")
        
        # Test alternative selectors
        alternative_selectors = [
            '.fc-list-event',
            '.fc-timegrid-event', 
            '.fc-daygrid-event',
            '.fc-event-harness',
            '[data-event-id]',
            '.event-item',
            '.calendar-event',
            'a[href*="/event/"]',
            '.fc-event-main'
        ]
        
        for selector in alternative_selectors:
            try:
                elements = browser.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                else:
                    print(f"❌ No elements found with selector: {selector}")
            except Exception as e:
                print(f"❌ Error with selector {selector}: {e}")
        
        print("\n🔍 Testing data attributes...")
        
        # Test data attributes
        data_elements = browser.find_elements(By.CSS_SELECTOR, '[data-events], [data-calendar], [data-schedule]')
        print(f"Found {len(data_elements)} elements with data attributes")
        
        for elem in data_elements[:3]:  # Check first 3
            try:
                data_events = elem.get_attribute('data-events')
                data_calendar = elem.get_attribute('data-calendar')
                data_schedule = elem.get_attribute('data-schedule')
                
                if data_events or data_calendar or data_schedule:
                    print(f"Found element with data: events={data_events}, calendar={data_calendar}, schedule={data_schedule}")
            except:
                continue
        
        print("\n🔍 Testing hidden inputs...")
        
        # Test hidden inputs
        hidden_inputs = browser.find_elements(By.CSS_SELECTOR, 'input[type="hidden"]')
        print(f"Found {len(hidden_inputs)} hidden inputs")
        
        for input_elem in hidden_inputs[:5]:  # Check first 5
            try:
                name = input_elem.get_attribute('name')
                value = input_elem.get_attribute('value')
                if name and ('event' in name.lower() or 'calendar' in name.lower()):
                    print(f"Hidden input: {name} = {value[:100]}")
            except:
                continue
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    finally:
        browser.quit()

if __name__ == "__main__":
    test_reverse_engineering_methods()
