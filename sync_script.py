#!/usr/bin/env python3
"""
Clean Subsplash to Google Calendar Sync Script
Based on the working scraper that successfully found events using 'a.fc-event' selector
Fixed: Timezone conversion - treats scraped times as UTC and converts to Eastern Time
"""

import os
import json
import time
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pickle

# Google Calendar imports
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
from selenium.common.exceptions import TimeoutException

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Timezone handling
import pytz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SubsplashCalendarSync:
    """Clean implementation of Subsplash to Google Calendar sync"""
    
    def __init__(self):
        self.browser = None
        self.google_service = None
        
        # Configuration
        self.test_mode = os.getenv('TEST_MODE', 'false').lower() == 'true'
        self.max_months_to_check = int(os.getenv('MAX_MONTHS_TO_CHECK', '24'))
        self.browser_wait_time = int(os.getenv('BROWSER_WAIT_TIME', '15'))
        
        # Calendar configuration
        if self.test_mode:
            logger.info("🧪 TEST MODE ENABLED - Only scraping prayer calendar")
            self.calendar_ids = {
                'prayer': os.getenv('PRAYER_CALENDAR_ID'),
            }
            self.calendar_urls = {
                'prayer': 'https://antiochboone.com/calendar-prayer',
            }
        else:
            # Full production mode
            self.calendar_ids = {
                'prayer': os.getenv('PRAYER_CALENDAR_ID'),
                'bam': os.getenv('BAM_CALENDAR_ID'),
                'kids': os.getenv('KIDS_CALENDAR_ID'),
                'college': os.getenv('COLLEGE_CALENDAR_ID'),
                'adt': os.getenv('ADT_CALENDAR_ID'),
                'missions': os.getenv('MISSIONS_CALENDAR_ID'),
                'youth': os.getenv('YOUTH_CALENDAR_ID'),
                'women': os.getenv('WOMEN_CALENDAR_ID'),
                'men': os.getenv('MEN_CALENDAR_ID'),
                'lifegroup': os.getenv('LIFEGROUP_CALENDAR_ID'),
                'staff': os.getenv('STAFF_CALENDAR_ID'),
                'elder': os.getenv('ELDER_CALENDAR_ID'),
                'worship': os.getenv('WORSHIP_CALENDAR_ID'),
                'prophetic': os.getenv('PROPHETIC_CALENDAR_ID'),
                'teaching': os.getenv('TEACHING_CALENDAR_ID'),
                'churchwide': os.getenv('CHURCHWIDE_CALENDAR_ID'),
                'hub': os.getenv('HUB_CALENDAR_ID')
            }
            self.calendar_urls = {
                'prayer': 'https://antiochboone.com/calendar-prayer',
                'bam': 'https://antiochboone.com/calendar-bam',
                'kids': 'https://antiochboone.com/calendar-kids',
                'college': 'https://antiochboone.com/calendar-college',
                'adt': 'https://antiochboone.com/calendar-adt',
                'missions': 'https://antiochboone.com/calendar-missions',
                'youth': 'https://antiochboone.com/calendar-youth',
                'women': 'https://antiochboone.com/calendar-women',
                'men': 'https://antiochboone.com/calendar-men',
                'lifegroup': 'https://antiochboone.com/calendar-lifegroup',
                'staff': 'https://antiochboone.com/calendar-staff',
                'elder': 'https://antiochboone.com/calendar-elder',
                'worship': 'https://antiochboone.com/calendar-worship',
                'prophetic': 'https://antiochboone.com/calendar-prophetic',
                'teaching': 'https://antiochboone.com/calendar-teaching',
                'churchwide': 'https://antiochboone.com/calendar-churchwide',
                'hub': 'https://antiochboone.com/calendar-hub'
            }
    
    def setup_browser(self):
        """Setup Chrome browser for web scraping"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            if os.getenv('GITHUB_ACTIONS') == 'true':
                # GitHub Actions specific options
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--disable-plugins')
                chrome_options.add_argument('--disable-images')
            
            service = Service(ChromeDriverManager().install())
            self.browser = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✅ Browser setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {str(e)}")
            return False
    
    def authenticate_google(self):
        """Authenticate with Google Calendar API using OAuth 2.0"""
        try:
            # Use OAuth 2.0 authentication
            from google_auth_oauthlib.flow import InstalledAppFlow
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            
            creds = None
            if os.path.exists('token.pickle'):
                try:
                    with open('token.pickle', 'rb') as token:
                        creds = pickle.load(token)
                    logger.info("✅ Loaded existing OAuth token")
                except Exception as e:
                    logger.warning(f"Could not load existing token: {str(e)}")
                    creds = None
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("🔄 Refreshing expired OAuth token...")
                    creds.refresh(Request())
                    logger.info("✅ OAuth token refreshed successfully")
                else:
                    logger.info("🔐 Starting OAuth 2.0 flow...")
                    # For GitHub Actions, we need to handle headless authentication
                    if os.getenv('GITHUB_ACTIONS') == 'true':
                        logger.error("❌ OAuth 2.0 interactive flow not supported in GitHub Actions")
                        logger.info("💡 Use service account credentials for GitHub Actions")
                        return False
                    else:
                        # Local development - interactive OAuth flow
                        flow = InstalledAppFlow.from_client_secrets_file(
                            'credentials.json', SCOPES)
                        creds = flow.run_local_server(port=0)
                        logger.info("✅ OAuth 2.0 flow completed")
                
                # Save the credentials for next run
                try:
                    with open('token.pickle', 'wb') as token:
                        pickle.dump(creds, token)
                    logger.info("💾 OAuth token saved for future use")
                except Exception as e:
                    logger.warning(f"Could not save token: {str(e)}")
            
            self.google_service = build('calendar', 'v3', credentials=creds)
            logger.info("✅ Google Calendar API service created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Google authentication failed: {str(e)}")
            return False
    
    def scrape_calendar(self, calendar_type: str) -> List[Dict]:
        """Scrape events from a specific Subsplash calendar using the working selector"""
        try:
            url = self.calendar_urls.get(calendar_type)
            if not url:
                logger.error(f"Unknown calendar type: {calendar_type}")
                return []
            
            logger.info(f"🔍 Scraping {calendar_type} calendar: {url}")
            
            # Navigate to the calendar page
            self.browser.get(url)
            time.sleep(3)  # Wait for page to load
            
            # Wait for calendar to load
            try:
                WebDriverWait(self.browser, self.browser_wait_time).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.fc-daygrid-body, .fc-view-container'))
                )
                logger.info("✅ Calendar container found")
                time.sleep(3)  # Wait for FullCalendar to render events
            except TimeoutException:
                logger.warning("❌ Calendar container not found, proceeding anyway...")
            
            # Use the working selector that was successful in your debug
            logger.info("🔍 Using working FullCalendar event selector: 'a.fc-event'")
            event_elements = self.browser.find_elements(By.CSS_SELECTOR, 'a.fc-event')
            
            if not event_elements:
                logger.warning("❌ No events found with selector 'a.fc-event'")
                return []
            
            logger.info(f"✅ Found {len(event_elements)} events using selector: a.fc-event")
            
            # Extract events from current month view
            events = self._extract_month_events(event_elements, calendar_type)
            
            if self.test_mode:
                logger.info(f"🧪 TEST MODE: Scraped {len(events)} events from current month view")
            else:
                # Production mode: Check multiple months
                months_checked = 1
                empty_months = 0
                
                while months_checked < self.max_months_to_check and empty_months < 3:
                    logger.info(f"📅 Checking month {months_checked + 1}")
                    
                    if self._navigate_to_next_month():
                        months_checked += 1
                        time.sleep(2)  # Wait for month to load
                        
                        # Extract events from new month view
                        month_event_elements = self.browser.find_elements(By.CSS_SELECTOR, 'a.fc-event')
                        if month_event_elements:
                            month_events = self._extract_month_events(month_event_elements, calendar_type)
                            if month_events:
                                events.extend(month_events)
                                empty_months = 0
                                logger.info(f"✅ Found {len(month_events)} events in month {months_checked}")
                            else:
                                empty_months += 1
                        else:
                            empty_months += 1
                    else:
                        logger.warning("Could not navigate to next month")
                        break
            
            logger.info(f"🎯 Total events scraped: {len(events)}")
            return events
            
        except Exception as e:
            logger.error(f"❌ Error scraping {calendar_type} calendar: {str(e)}")
            return []
    
    def _extract_month_events(self, event_elements: List, calendar_type: str) -> List[Dict]:
        """Extract event data from FullCalendar event elements"""
        events = []
        
        for i, element in enumerate(event_elements):
            try:
                logger.debug(f"Processing event element {i}")
                
                # Extract event data using the working method from your debug
                event_data = self._extract_fc_event(element, calendar_type)
                
                if event_data:
                    events.append(event_data)
                    logger.debug(f"✅ Extracted event: {event_data.get('title', 'Unknown')}")
                else:
                    logger.debug(f"⚠️ Could not extract event from element {i}")
                    
            except Exception as e:
                logger.warning(f"Error processing event element {i}: {str(e)}")
                continue
        
        return events
    
    def _extract_fc_event(self, event_element, calendar_type: str) -> Optional[Dict]:
        """Extract event data from a FullCalendar event element using working logic"""
        try:
            # Get event text content
            event_text = event_element.text.strip()
            if not event_text:
                return None
            
            # Get event URL
            event_url = event_element.get_attribute('href')
            if event_url and not event_url.startswith('http'):
                event_url = f"https://antiochboone.com{event_url}"
            
            # Get event ID
            event_id = event_element.get_attribute('data-id')
            
            # Parse time and title from event text
            time_match = None
            title = event_text
            
            # Look for time patterns (e.g., "9:15p", "10:30a")
            time_patterns = [
                r'(\d{1,2}:\d{2}[ap]m?)',  # 9:15p, 10:30a
                r'(\d{1,2}:\d{2})',        # 9:15, 10:30
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, event_text, re.IGNORECASE)
                if match:
                    time_match = match.group(1)
                    # Remove time from title
                    title = event_text.replace(time_match, '').strip()
                    break
            
            if not time_match:
                logger.debug(f"No time found in event: {event_text}")
                return None
            
            # Get the actual date from the calendar day where this event appears
            event_date = self._get_event_date(event_element)
            if not event_date:
                logger.warning(f"Could not determine date for event: {event_text}")
                return None
            
            # Parse the time and apply timezone conversion with the actual date
            event_time = self._parse_and_convert_time(time_match, event_date)
            if not event_time:
                return None
            
            # Create event data
            event_data = {
                'title': title,
                'time': time_match,
                'date': event_date.strftime('%Y-%m-%d'),
                'datetime': event_time.isoformat(),
                'url': event_url,
                'id': event_id,
                'calendar_type': calendar_type,
                'source': 'subsplash'
            }
            
            return event_data
            
        except Exception as e:
            logger.warning(f"Error extracting event data: {str(e)}")
            return None
    
    def _get_event_date(self, event_element) -> Optional[datetime]:
        """Extract the actual date from the calendar day where the event appears"""
        try:
            # Find the parent calendar day element that contains this event
            # FullCalendar typically has a structure like: .fc-day -> .fc-daygrid-day -> .fc-daygrid-day-events -> .fc-event
            day_element = event_element.find_element(By.XPATH, "./ancestor::td[contains(@class, 'fc-day')]")
            
            # Get the date from the day element's data attribute or aria-label
            date_attr = day_element.get_attribute('data-date')
            if date_attr:
                # data-date is typically in YYYY-MM-DD format
                return datetime.strptime(date_attr, '%Y-%m-%d')
            
            # Alternative: look for aria-label with date info
            aria_label = day_element.get_attribute('aria-label')
            if aria_label:
                # aria-label might contain date info like "Tuesday, August 26, 2025"
                # Try to parse common date formats
                import re
                date_patterns = [
                    r'(\w+), (\w+) (\d{1,2}), (\d{4})',  # Tuesday, August 26, 2025
                    r'(\w+) (\d{1,2}), (\d{4})',          # August 26, 2025
                ]
                
                for pattern in date_patterns:
                    match = re.search(pattern, aria_label)
                    if match:
                        if len(match.groups()) == 4:
                            # Tuesday, August 26, 2025
                            month_name, day, year = match.group(2), match.group(3), match.group(4)
                        else:
                            # August 26, 2025
                            month_name, day, year = match.group(1), match.group(2), match.group(3)
                        
                        # Convert month name to number
                        month_map = {
                            'january': 1, 'february': 2, 'march': 3, 'april': 4,
                            'may': 5, 'june': 6, 'july': 7, 'august': 8,
                            'september': 9, 'october': 10, 'november': 11, 'december': 12
                        }
                        
                        month = month_map.get(month_name.lower())
                        if month:
                            return datetime(int(year), month, int(day))
            
            # If we can't find the date, log a warning and return None
            logger.warning(f"Could not extract date from calendar day element")
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting event date: {str(e)}")
            return None
    
    def _parse_and_convert_time(self, time_str: str, event_date: datetime) -> Optional[datetime]:
        """Parse time string and apply timezone conversion (UTC to Eastern Time)"""
        try:
            # Parse time string - handle both formats
            original_time = time_str
            time_str = time_str.lower()
            
            # Handle different time formats
            if time_str.endswith('p') and not time_str.endswith('pm'):
                time_str = time_str[:-1] + 'pm'
            elif time_str.endswith('a') and not time_str.endswith('am'):
                time_str = time_str[:-1] + 'am'
            
            # Try different time formats
            time_formats = [
                '%I:%M%p',  # 9:15pm
                '%I:%M %p', # 9:15 pm
                '%H:%M',    # 21:15
            ]
            
            parsed_time = None
            for fmt in time_formats:
                try:
                    parsed_time = datetime.strptime(time_str, fmt)
                    break
                except ValueError:
                    continue
            
            if not parsed_time:
                logger.warning(f"Could not parse time: {time_str}")
                return None
            
            # Apply timezone conversion (fix for 4-hour offset)
            # The scraper pulls times in UTC, but they display as if they're Eastern Time
            # So we need to convert FROM UTC TO Eastern Time (subtract 4/5 hours depending on DST)
            utc_tz = pytz.timezone('UTC')
            est_tz = pytz.timezone('US/Eastern')
            
            # Create a datetime object for the actual event date with the parsed time
            event_datetime = datetime.combine(event_date.date(), parsed_time.time())
            
            # First, treat the time as UTC (this is what the scraper actually gets)
            utc_datetime = utc_tz.localize(event_datetime)
            
            # Then convert to Eastern Time (this subtracts 4 hours during EDT, 5 hours during EST)
            eastern_datetime = utc_datetime.astimezone(est_tz)
            
            logger.debug(f"Time conversion: {original_time} on {event_date.strftime('%Y-%m-%d')} UTC -> {utc_datetime} -> {eastern_datetime} Eastern")
            
            return eastern_datetime
            
        except Exception as e:
            logger.error(f"Error parsing/converting time {time_str}: {str(e)}")
            return None
    
    def _navigate_to_next_month(self) -> bool:
        """Navigate to the next month in the calendar"""
        try:
            # Look for next month button
            next_button = self.browser.find_element(By.CSS_SELECTOR, 
                '.fc-next-button, [aria-label*="next"], .fc-icon-chevron-right')
            
            if next_button and next_button.is_enabled():
                next_button.click()
                time.sleep(2)  # Wait for navigation
                return True
            else:
                logger.info("Next month button not available or disabled")
                return False
                
        except Exception as e:
            logger.warning(f"Could not navigate to next month: {str(e)}")
            return False
    
    def sync_to_google_calendar(self, events: List[Dict], calendar_type: str):
        """Sync scraped events to Google Calendar"""
        if not self.google_service:
            logger.error("❌ Google service not authenticated")
            return False
        
        calendar_id = self.calendar_ids.get(calendar_type)
        if not calendar_id:
            logger.error(f"❌ No Google Calendar ID for {calendar_type}")
            return False
        
        logger.info(f"🔄 Syncing {len(events)} events to Google Calendar: {calendar_id}")
        
        synced_count = 0
        for event in events:
            try:
                # Create Google Calendar event
                google_event = {
                    'summary': event['title'],
                    'description': f"Source: {event.get('url', 'N/A')}",
                    'start': {
                        'dateTime': event['datetime'],
                        'timeZone': 'America/New_York',
                    },
                    'end': {
                        'dateTime': (datetime.fromisoformat(event['datetime']) + timedelta(hours=1)).isoformat(),
                        'timeZone': 'America/New_York',
                    },
                    'source': {
                        'title': 'Subsplash Calendar',
                        'url': event.get('url', '')
                    }
                }
                
                # Insert event into Google Calendar
                result = self.google_service.events().insert(
                    calendarId=calendar_id,
                    body=google_event
                ).execute()
                
                synced_count += 1
                logger.info(f"✅ Synced event: {event['title']} at {event['time']}")
                
            except HttpError as e:
                if e.resp.status == 409:  # Event already exists
                    logger.debug(f"Event already exists: {event['title']}")
                else:
                    logger.error(f"❌ Error syncing event {event['title']}: {str(e)}")
            except Exception as e:
                logger.error(f"❌ Unexpected error syncing event {event['title']}: {str(e)}")
        
        logger.info(f"🎯 Successfully synced {synced_count}/{len(events)} events")
        return synced_count > 0
    
    def run_sync(self):
        """Main sync process"""
        try:
            logger.info("🚀 Starting Subsplash Calendar Sync")
            
            # Setup browser
            if not self.setup_browser():
                return False
            
            # Authenticate with Google (both test and production modes)
            if not self.authenticate_google():
                logger.error("❌ Google authentication failed, cannot proceed")
                return False
            
            # Sync each calendar
            for calendar_type in self.calendar_urls.keys():
                try:
                    logger.info(f"🔄 Processing {calendar_type} calendar...")
                    
                    # Scrape events
                    events = self.scrape_calendar(calendar_type)
                    
                    if events:
                        # Log events for debugging
                        logger.info(f"✅ Found {len(events)} events")
                        for i, event in enumerate(events[:3]):
                            logger.info(f"  Event {i+1}: {event['title']} at {event['time']} -> {event['datetime']}")
                        
                        # Sync to Google Calendar
                        self.sync_to_google_calendar(events, calendar_type)
                    else:
                        logger.info(f"⚠️ No events found for {calendar_type} calendar")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing {calendar_type} calendar: {str(e)}")
                    continue
            
            logger.info("✅ Calendar sync completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fatal error during sync: {str(e)}")
            return False
        
        finally:
            if self.browser:
                self.browser.quit()
                logger.info("🔒 Browser closed")

def main():
    """Main entry point"""
    sync = SubsplashCalendarSync()
    success = sync.run_sync()
    
    if success:
        logger.info("🎉 Sync completed successfully")
        exit(0)
    else:
        logger.error("💥 Sync failed")
        exit(1)

if __name__ == "__main__":
    main()