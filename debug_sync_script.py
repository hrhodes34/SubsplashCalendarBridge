#!/usr/bin/env python3
"""
Debug Version of Subsplash Calendar Sync Script
This version provides detailed logging to diagnose issues
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pickle

# Google Calendar imports
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Web scraping imports
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DebugSubsplashCalendarSync:
    """Debug version with detailed logging"""
    
    def __init__(self):
        self.driver = None
        self.google_service = None
        self.calendar_ids = {
            'prayer': os.getenv('PRAYER_CALENDAR_ID'),
            'bam': os.getenv('BAM_CALENDAR_ID'),
            'kids': os.getenv('KIDS_CALENDAR_ID'),
        }
        
        # Only test with prayer calendar for now
        self.calendar_urls = {
            'prayer': 'https://antiochboone.com/calendar-prayer',
        }
        
        logger.info("🔍 DEBUG MODE: Initialized debug scraper")
        logger.info(f"Calendar IDs: {self.calendar_ids}")
    
    def setup_browser(self) -> bool:
        """Setup Chrome browser for web scraping"""
        try:
            chrome_options = Options()
            
            # Debug mode - visible browser
            # chrome_options.add_argument('--headless')
            
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("✅ Browser setup successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {str(e)}")
            return False
    
    def get_current_month_year(self) -> Tuple[str, str]:
        """Get the current month and year displayed in the calendar"""
        try:
            month_year_element = self.driver.find_element(By.CLASS_NAME, "fc-toolbar-title")
            month_year_text = month_year_element.text.strip()
            logger.debug(f"📅 Calendar header shows: '{month_year_text}'")
            
            parts = month_year_text.split()
            if len(parts) == 2:
                month = parts[0]
                year = parts[1]
                logger.debug(f"📅 Parsed: Month='{month}', Year='{year}'")
                return month, year
            else:
                logger.warning(f"⚠️ Unexpected month/year format: '{month_year_text}'")
                return "Unknown", "Unknown"
                
        except Exception as e:
            logger.error(f"❌ Error getting current month/year: {str(e)}")
            return "Unknown", "Unknown"
    
    def scrape_current_month_events(self, calendar_type: str) -> List[Dict]:
        """Scrape events from the currently displayed month with detailed logging"""
        events = []
        
        try:
            month, year = self.get_current_month_year()
            logger.info(f"🔍 Scraping {calendar_type} events for {month} {year}")
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Look specifically for FullCalendar events
            fc_events = soup.find_all('a', class_='fc-event')
            logger.info(f"🔍 Found {len(fc_events)} FullCalendar event elements")
            
            # Save HTML for inspection
            with open(f'debug_{calendar_type}_{month}_{year}.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            logger.info(f"💾 Saved debug HTML to debug_{calendar_type}_{month}_{year}.html")
            
            for i, event_element in enumerate(fc_events):
                try:
                    logger.debug(f"🔍 Processing event element {i+1}:")
                    logger.debug(f"   Raw HTML: {str(event_element)[:200]}...")
                    
                    event = self._extract_fc_event_debug(event_element, month, year, calendar_type)
                    if event:
                        events.append(event)
                        logger.info(f"✅ Event {i+1}: {event['title']} on {event['start']}")
                        logger.debug(f"   Full event data: {json.dumps(event, indent=2, default=str)}")
                    else:
                        logger.warning(f"⚠️ Event {i+1}: Failed to extract")
                        
                except Exception as e:
                    logger.error(f"❌ Error extracting event {i+1}: {str(e)}")
                    continue
            
            return events
            
        except Exception as e:
            logger.error(f"❌ Error scraping current month events: {str(e)}")
            return events
    
    def _extract_fc_event_debug(self, event_element, month: str, year: str, calendar_type: str) -> Optional[Dict]:
        """Extract event data with detailed debugging"""
        try:
            logger.debug("🔍 Starting event extraction...")
            
            # Get the event title
            title_element = event_element.find('div', class_='fc-event-title')
            if not title_element:
                logger.debug("❌ No title element found")
                return None
            
            title = title_element.get_text(strip=True)
            if not title:
                logger.debug("❌ Title is empty")
                return None
            
            logger.debug(f"📝 Title found: '{title}'")
            
            # Get the event time
            time_element = event_element.find('div', class_='fc-event-time')
            time_str = time_element.get_text(strip=True) if time_element else ""
            logger.debug(f"⏰ Time found: '{time_str}'")
            
            # Get the date from the parent day cell
            date_cell = event_element.find_parent('td', attrs={'data-date': True})
            if not date_cell:
                logger.debug("❌ No date cell found")
                return None
            
            date_str = date_cell.get('data-date')
            if not date_str:
                logger.debug("❌ No date attribute found")
                return None
            
            logger.debug(f"📅 Date found: '{date_str}'")
            
            # Parse the date
            try:
                event_date = datetime.strptime(date_str, '%Y-%m-%d')
                logger.debug(f"📅 Parsed date: {event_date}")
            except ValueError:
                logger.warning(f"⚠️ Could not parse date: '{date_str}'")
                return None
            
            # Parse the time
            start_time, end_time = self._parse_fc_time_debug(time_str, event_date)
            logger.debug(f"⏰ Parsed times: Start={start_time}, End={end_time}")
            
            # Get event URL if available
            event_url = event_element.get('href', '')
            logger.debug(f"🔗 URL found: '{event_url}'")
            
            # Create event object
            event = {
                'title': title,
                'start': start_time,
                'end': end_time,
                'date': date_str,
                'time': time_str,
                'month': month,
                'year': year,
                'calendar_type': calendar_type,
                'url': event_url,
                'all_day': self._is_all_day_event(start_time, end_time),
                'source': 'Subsplash',
                'location': 'Antioch Boone'
            }
            
            logger.debug(f"✅ Event extraction successful: {event}")
            return event
            
        except Exception as e:
            logger.error(f"❌ Error extracting FC event: {str(e)}")
            return None
    
    def _parse_fc_time_debug(self, time_str: str, event_date: datetime) -> Tuple[datetime, datetime]:
        """Parse FullCalendar time format with detailed debugging"""
        try:
            logger.debug(f"🔍 Parsing time: '{time_str}' for date: {event_date}")
            
            if not time_str:
                logger.debug("⏰ No time specified, treating as all-day event")
                start_time = event_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(days=1)
                return start_time, end_time
            
            # Parse time formats like "6:30a", "5:15p", "10:00"
            time_str = time_str.lower().strip()
            logger.debug(f"⏰ Normalized time string: '{time_str}'")
            
            # Handle AM/PM
            if 'a' in time_str:
                time_str = time_str.replace('a', '').strip()
                hour = int(time_str.split(':')[0])
                if hour == 12:
                    hour = 0
                minute = int(time_str.split(':')[1])
                logger.debug(f"⏰ AM time: Hour={hour}, Minute={minute}")
            elif 'p' in time_str:
                time_str = time_str.replace('p', '').strip()
                hour = int(time_str.split(':')[0])
                if hour != 12:
                    hour += 12
                minute = int(time_str.split(':')[1])
                logger.debug(f"⏰ PM time: Hour={hour}, Minute={minute}")
            else:
                # 24-hour format
                hour, minute = map(int, time_str.split(':'))
                logger.debug(f"⏰ 24-hour time: Hour={hour}, Minute={minute}")
            
            # Create start time
            start_time = event_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            logger.debug(f"⏰ Start time: {start_time}")
            
            # Default duration: 1 hour
            end_time = start_time + timedelta(hours=1)
            logger.debug(f"⏰ End time: {end_time}")
            
            return start_time, end_time
            
        except Exception as e:
            logger.warning(f"⚠️ Error parsing time '{time_str}': {str(e)}")
            # Fallback: create all-day event
            start_time = event_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=1)
            logger.debug(f"⏰ Fallback to all-day: Start={start_time}, End={end_time}")
            return start_time, end_time
    
    def _is_all_day_event(self, start_time: datetime, end_time: datetime) -> bool:
        """Check if event is all-day based on start and end times"""
        if not start_time or not end_time:
            return False
        
        return (start_time.hour == 0 and start_time.minute == 0 and 
                end_time.hour == 0 and end_time.minute == 0)
    
    def run_debug_scrape(self) -> List[Dict]:
        """Run a debug scrape of just the prayer calendar"""
        all_events = []
        
        try:
            if not self.setup_browser():
                return all_events
            
            # Only test prayer calendar for now
            calendar_type = 'prayer'
            calendar_url = self.calendar_urls.get(calendar_type)
            
            logger.info(f"🔍 Navigating to {calendar_type} calendar: {calendar_url}")
            self.driver.get(calendar_url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Start with current month
            current_month, current_year = self.get_current_month_year()
            logger.info(f"📅 Starting with current month: {current_month} {current_year}")
            
            # Scrape current month
            current_events = self.scrape_current_month_events(calendar_type)
            all_events.extend(current_events)
            logger.info(f"📊 Collected {len(current_events)} events from {current_month}")
            
            # Save all events to debug file
            with open('debug_events_found.json', 'w') as f:
                json.dump(all_events, f, indent=2, default=str)
            logger.info("💾 Saved all events to debug_events_found.json")
            
            return all_events
            
        except Exception as e:
            logger.error(f"❌ Error during debug scrape: {str(e)}")
            return all_events
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Main debug function"""
    logger.info("🔍 Starting Debug Subsplash Calendar Scrape")
    
    # Create debug sync instance
    sync = DebugSubsplashCalendarSync()
    
    # Run debug scrape
    events = sync.run_debug_scrape()
    
    # Display results
    print("\n" + "="*80)
    print("🔍 DEBUG SCRAPING RESULTS")
    print("="*80)
    
    if events:
        print(f"✅ Found {len(events)} events!")
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
        print("❌ No events found")
    
    print("="*80)
    print("🔍 Check the debug files:")
    print("  - debug_events_found.json (all events found)")
    print("  - debug_prayer_*.html (raw HTML for each month)")
    print("📝 Review the detailed logs above")

if __name__ == "__main__":
    main()
