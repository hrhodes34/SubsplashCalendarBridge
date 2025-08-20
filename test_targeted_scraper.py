#!/usr/bin/env python3
"""
Targeted Scraper for Subsplash FullCalendar Events
This script specifically targets the FullCalendar widget structure we found
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import re

# Web scraping imports
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TargetedSubsplashScraper:
    """Targeted scraper that specifically looks for FullCalendar events"""
    
    def __init__(self, calendar_url: str):
        self.calendar_url = calendar_url
        self.driver = None
        
        logger.info(f"Initialized targeted scraper for: {calendar_url}")
    
    def setup_browser(self) -> bool:
        """Setup Chrome browser for web scraping"""
        try:
            chrome_options = Options()
            
            # For testing, we'll use visible browser to see what's happening
            # chrome_options.add_argument('--headless')
            
            # Additional options for stability
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # Setup Chrome driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("Browser setup successful")
            return True
            
        except Exception as e:
            logger.error(f"Browser setup failed: {str(e)}")
            return False
    
    def scrape_fullcalendar_events(self) -> List[Dict]:
        """Scrape events specifically from the FullCalendar widget"""
        events = []
        
        try:
            # Wait for calendar content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "fc-event"))
            )
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            logger.info(f"Page loaded successfully. Content length: {len(page_source)} characters")
            
            # Save HTML for inspection
            with open('targeted_page_source.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            logger.info("Saved page source to targeted_page_source.html")
            
            # Look specifically for FullCalendar events
            fc_events = soup.find_all('a', class_='fc-event')
            logger.info(f"Found {len(fc_events)} FullCalendar events")
            
            for i, event_element in enumerate(fc_events):
                try:
                    event = self._extract_fc_event(event_element)
                    if event:
                        events.append(event)
                        logger.info(f"  Event {i+1}: {event['title']} on {event['start']}")
                except Exception as e:
                    logger.warning(f"Error extracting event {i+1}: {str(e)}")
                    continue
            
            return events
            
        except Exception as e:
            logger.error(f"Error extracting FullCalendar events: {str(e)}")
            return events
    
    def _extract_fc_event(self, event_element) -> Optional[Dict]:
        """Extract event data from a FullCalendar event element"""
        try:
            # Get the event title
            title_element = event_element.find('div', class_='fc-event-title')
            if not title_element:
                return None
            
            title = title_element.get_text(strip=True)
            if not title:
                return None
            
            # Get the event time
            time_element = event_element.find('div', class_='fc-event-time')
            time_str = time_element.get_text(strip=True) if time_element else ""
            
            # Get the date from the parent day cell
            date_cell = event_element.find_parent('td', attrs={'data-date': True})
            if not date_cell:
                return None
            
            date_str = date_cell.get('data-date')  # Format: "2025-08-21"
            if not date_str:
                return None
            
            # Parse the date
            try:
                event_date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                logger.warning(f"Could not parse date: {date_str}")
                return None
            
            # Parse the time
            start_time, end_time = self._parse_fc_time(time_str, event_date)
            
            # Get event URL if available
            event_url = event_element.get('href', '')
            
            # Create event object
            event = {
                'title': title,
                'start': start_time,
                'end': end_time,
                'date': date_str,
                'time': time_str,
                'url': event_url,
                'all_day': self._is_all_day_event(start_time, end_time),
                'raw_html': str(event_element)[:200] + "..."  # Include raw HTML for debugging
            }
            
            return event
            
        except Exception as e:
            logger.warning(f"Error extracting FC event: {str(e)}")
            return None
    
    def _parse_fc_time(self, time_str: str, event_date: datetime) -> Tuple[datetime, datetime]:
        """Parse FullCalendar time format and return start/end times"""
        try:
            if not time_str:
                # No time specified, treat as all-day event
                start_time = event_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(days=1)
                return start_time, end_time
            
            # Parse time formats like "6:30a", "5:15p", "10:00"
            time_str = time_str.lower().strip()
            
            # Handle AM/PM
            if 'a' in time_str:
                time_str = time_str.replace('a', '').strip()
                hour = int(time_str.split(':')[0])
                if hour == 12:
                    hour = 0
                minute = int(time_str.split(':')[1])
            elif 'p' in time_str:
                time_str = time_str.replace('p', '').strip()
                hour = int(time_str.split(':')[0])
                if hour != 12:
                    hour += 12
                minute = int(time_str.split(':')[1])
            else:
                # 24-hour format
                hour, minute = map(int, time_str.split(':'))
            
            # Create start time
            start_time = event_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Default duration: 1 hour
            end_time = start_time + timedelta(hours=1)
            
            return start_time, end_time
            
        except Exception as e:
            logger.warning(f"Error parsing time '{time_str}': {str(e)}")
            # Fallback: create all-day event
            start_time = event_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=1)
            return start_time, end_time
    
    def _is_all_day_event(self, start_time: datetime, end_time: datetime) -> bool:
        """Check if event is all-day based on start and end times"""
        if not start_time or not end_time:
            return False
        
        # Check if times are midnight (all-day events typically start/end at midnight)
        return (start_time.hour == 0 and start_time.minute == 0 and 
                end_time.hour == 0 and end_time.minute == 0)
    
    def run_targeted_scrape(self) -> List[Dict]:
        """Run a targeted scrape of the FullCalendar"""
        events = []
        
        try:
            if not self.setup_browser():
                return events
            
            # Navigate to the calendar page
            logger.info(f"Navigating to: {self.calendar_url}")
            self.driver.get(self.calendar_url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Extract FullCalendar events
            events = self.scrape_fullcalendar_events()
            
            return events
            
        except Exception as e:
            logger.error(f"Error during targeted scrape: {str(e)}")
            return events
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Main test function"""
    logger.info("🎯 Starting Targeted FullCalendar Scrape")
    
    # Test with the Prayer calendar (which should have the events we know about)
    test_url = "https://antiochboone.com/calendar-prayer"
    
    logger.info(f"Testing with URL: {test_url}")
    logger.info("Expected events:")
    logger.info("  - 8/21 6:30 AM Early Morning Prayer")
    logger.info("  - 8/26 5:15 PM Prayer Set") 
    logger.info("  - 8/28 6:30 AM Early Morning Prayer")
    
    # Create scraper and run test
    scraper = TargetedSubsplashScraper(test_url)
    events = scraper.run_targeted_scrape()
    
    # Display results
    print("\n" + "="*80)
    print("🎯 TARGETED SCRAPING RESULTS")
    print("="*80)
    
    if events:
        print(f"✅ Successfully found {len(events)} FullCalendar events!")
        print()
        
        for i, event in enumerate(events, 1):
            print(f"Event {i}:")
            print(f"  Title: {event['title']}")
            print(f"  Date: {event['date']}")
            print(f"  Time: {event['time']}")
            print(f"  Start: {event['start']}")
            print(f"  End: {event['end']}")
            print(f"  All Day: {event['all_day']}")
            print(f"  URL: {event['url']}")
            print()
    else:
        print("❌ No FullCalendar events found")
        print("\nThis could mean:")
        print("- The FullCalendar widget hasn't loaded yet")
        print("- The selectors need to be updated")
        print("- The page structure is different than expected")
        print("\nCheck the saved HTML file 'targeted_page_source.html' for manual inspection")
    
    print("="*80)
    print("🔍 Check 'targeted_page_source.html' for the raw page content")
    print("📝 Review the logs above for detailed extraction information")

if __name__ == "__main__":
    main()
