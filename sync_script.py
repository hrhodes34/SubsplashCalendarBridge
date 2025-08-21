#!/usr/bin/env python3
"""
Simplified Subsplash to Google Calendar Sync Script
This script automatically scrapes events from Subsplash calendars and syncs them to Google Calendar
Fixed: 4-hour time offset issue by applying timezone correction

TEST MODE: Currently configured to only scrape August prayer calendar for testing
"""

import os
import json
import time
import logging
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
    level=logging.DEBUG,  # Enable debug logging to see raw text
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SubsplashCalendarSync:
    """Simplified class for syncing Subsplash calendars to Google Calendar"""
    
    def __init__(self):
        self.browser = None
        self.google_service = None
        
        # TEST MODE: Only prayer calendar for testing
        self.test_mode = os.getenv('TEST_MODE', 'true').lower() == 'true'
        
        if self.test_mode:
            logger.info("🧪 TEST MODE ENABLED - Only scraping prayer calendar for August")
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
        
        # Configuration
        if self.test_mode:
            # TEST MODE: Only check August
            self.max_months_to_check = 1
            self.target_month = 'August'
            self.target_year = '2025'
        else:
            # Production mode: Check multiple months
            self.max_months_to_check = int(os.getenv('MAX_MONTHS_TO_CHECK', '6'))
        
        self.browser_wait_time = int(os.getenv('BROWSER_WAIT_TIME', '10'))
        
        if self.test_mode:
            logger.info("🧪 Initialized TEST MODE Subsplash Calendar Sync")
            logger.info(f"🎯 Target: {self.target_month} {self.target_year} - Prayer Calendar Only")
        else:
            logger.info("🚀 Initialized Production Subsplash Calendar Sync")
    
    def setup_browser(self) -> bool:
        """Setup Chrome browser for web scraping"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Use webdriver manager to handle Chrome driver
            service = Service(ChromeDriverManager().install())
            self.browser = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("✅ Browser setup successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {str(e)}")
            return False
    
    def authenticate_google(self) -> bool:
        """Authenticate with Google Calendar API"""
        try:
            # Check for OAuth credentials file
            credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
            token_file = os.getenv('GOOGLE_TOKEN_FILE', 'token.pickle')
            
            if not os.path.exists(credentials_file):
                logger.error(f"OAuth credentials file {credentials_file} not found")
                return False
            
            # Load OAuth 2.0 credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            import pickle
            
            creds = None
            
            # Try to load existing token
            if os.path.exists(token_file):
                try:
                    with open(token_file, 'rb') as token:
                        creds = pickle.load(token)
                    logger.info("Loaded existing OAuth token")
                except Exception as e:
                    logger.warning(f"Could not load existing token: {str(e)}")
                    creds = None
            
            # If no valid credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing expired OAuth token...")
                    creds.refresh(Request())
                else:
                    logger.info("Starting OAuth 2.0 flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_file, 
                        ['https://www.googleapis.com/auth/calendar']
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            # Build the service
            self.google_service = build('calendar', 'v3', credentials=creds)
            logger.info("✅ Google Calendar authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Google Calendar authentication failed: {str(e)}")
            return False
    
    def scrape_calendar_events(self, calendar_type: str) -> List[Dict]:
        """Scrape events from a specific Subsplash calendar"""
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
            WebDriverWait(self.browser, self.browser_wait_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.fc-daygrid-body, .fc-view-container'))
            )
<<<<<<< HEAD
            
            events = []
            
            if self.test_mode:
                # TEST MODE: Only scrape August
                logger.info(f"🧪 TEST MODE: Scraping only {self.target_month} {self.target_year}")
                events = self._scrape_august_events(calendar_type)
            else:
                # Production mode: Check multiple months
                months_checked = 0
                empty_months = 0
                
                # Check current month and next few months
                while months_checked < self.max_months_to_check and empty_months < 3:
                    logger.info(f"📅 Checking month {months_checked + 1}")
=======
            logger.info("✅ Calendar container found")
            # Additional wait for FullCalendar to render events
            logger.info("Waiting 3 seconds for FullCalendar to render events...")
            time.sleep(3)
        except TimeoutException:
            logger.warning("❌ Calendar container not found, proceeding anyway...")
            
            # Debug: Let's see what's actually on the page
            logger.info("🔍 DEBUG: Analyzing page structure...")
            try:
                page_title = self.browser.title
                logger.info(f"Page title: {page_title}")
                
                # Look for any calendar-related elements
                calendar_elements = self.browser.find_elements(By.CSS_SELECTOR, '[class*="calendar"], [class*="fc"], [class*="event"]')
                logger.info(f"Found {len(calendar_elements)} elements with calendar/event-related classes")
                
                # Check for common FullCalendar elements
                fc_elements = self.browser.find_elements(By.CSS_SELECTOR, '.fc-toolbar, .fc-view, .fc-day, .fc-event')
                logger.info(f"Found {len(fc_elements)} FullCalendar elements")
                
                # Log the first few elements for debugging
                for i, elem in enumerate(fc_elements[:5]):
                    try:
                        logger.info(f"FC Element {i}: {elem.tag_name} - class='{elem.get_attribute('class')}' - text='{elem.text[:100]}'")
                    except:
                        logger.info(f"FC Element {i}: Error getting info")
                        
            except Exception as debug_e:
                logger.error(f"Error during page analysis: {debug_e}")

        # Try the simple, working FullCalendar selector first
        event_selectors = [
            'a.fc-event',  # This is what actually works
        ]
        
        event_elements = []
        used_selector = None
        
        # Try the working selector
        logger.info("🔍 Trying FullCalendar event selector...")
        for selector in event_selectors:
            try:
                logger.info(f"  Trying selector: '{selector}'")
                elements = self.browser.find_elements(By.CSS_SELECTOR, selector)
                logger.info(f"  Found {len(elements)} elements with selector '{selector}'")
                
                if elements:
                    event_elements = elements
                    used_selector = selector
                    logger.info(f"✅ SUCCESS: Found {len(elements)} events using selector: {selector}")
>>>>>>> parent of b1d1c9c (stuf)
                    
                    # Extract events from current month view
                    month_events = self._extract_month_events(calendar_type)
                    
                    if month_events:
                        events.extend(month_events)
                        empty_months = 0
                        logger.info(f"✅ Found {len(month_events)} events in month {months_checked + 1}")
                    else:
                        empty_months += 1
                        logger.info(f"⚠️ No events found in month {months_checked + 1}")
                    
                    # Navigate to next month
                    if self._navigate_to_next_month():
                        months_checked += 1
                        time.sleep(2)  # Wait for month to load
                    else:
                        logger.warning("Could not navigate to next month")
                        break
            
            logger.info(f"🎯 Total events scraped: {len(events)}")
            return events
            
        except Exception as e:
            logger.error(f"❌ Error scraping {calendar_type} calendar: {str(e)}")
            return []
    
<<<<<<< HEAD
    def _scrape_august_events(self, calendar_type: str) -> List[Dict]:
        """TEST MODE: Scrape events specifically from August"""
=======
    def _deduplicate_event_elements(self, event_elements) -> List:
        """Deduplicate event elements to prevent multiple copies of the same event"""
        unique_elements = []
        seen_titles = set()
        
        for element in event_elements:
            try:
                # Get the text content directly
                title = element.text.strip()
                if not title or len(title) < 3:
                    continue
                
                # Simple deduplication: if we've seen this title before, skip it
                if title not in seen_titles:
                    seen_titles.add(title)
                    unique_elements.append(element)
                    logger.debug(f"Added unique event: {title}")
                else:
                    logger.debug(f"Skipped duplicate event: {title}")
                    
            except Exception as e:
                logger.debug(f"Error during deduplication: {e}")
                continue
        
        logger.info(f"Deduplication: {len(event_elements)} total elements -> {len(unique_elements)} unique elements")
        return unique_elements
    
    def _extract_fc_event(self, event_element, month: str, year: str, calendar_type: str) -> Optional[Dict]:
        """Extract event data from a FullCalendar event element"""
>>>>>>> parent of b1d1c9c (stuf)
        try:
            logger.info(f"🧪 Scraping {self.target_month} {self.target_year} events...")
            
<<<<<<< HEAD
            # Check if we're already in August
            current_month_year = self._get_current_month_year()
            logger.info(f"📅 Current view: {current_month_year}")
            
            # Navigate to August if needed
            if self.target_month not in current_month_year or self.target_year not in current_month_year:
                logger.info(f"🔄 Navigating to {self.target_month} {self.target_year}...")
                if not self._navigate_to_august():
                    logger.warning(f"Could not navigate to {self.target_month} {self.target_year}, will work with current view")
            
            # Extract events from current month view
            events = self._extract_month_events(calendar_type)
            
            if events:
                logger.info(f"✅ Found {len(events)} events in {self.target_month} {self.target_year}")
            else:
                logger.warning(f"⚠️ No events found in {self.target_month} {self.target_year}")
            
            return events
            
        except Exception as e:
            logger.error(f"Error scraping August events: {str(e)}")
            return []
    
    def _get_current_month_year(self) -> str:
        """Get the current month and year being displayed"""
        try:
            # Look for month/year display elements
            month_elements = self.browser.find_elements(By.CSS_SELECTOR, 
                '.fc-toolbar-title, [class*="month"], [class*="year"], h1, h2')
            
            for element in month_elements:
                text = element.text.strip()
                if text and ('August' in text or '2025' in text):
                    return text
            
            return "Unknown Month/Year"
            
        except Exception as e:
            logger.warning(f"Could not get current month/year: {str(e)}")
            return "Unknown Month/Year"
    
    def _navigate_to_august(self) -> bool:
        """TEST MODE: Navigate to August 2025"""
        try:
            # Look for navigation buttons
            next_button = self.browser.find_element(By.CSS_SELECTOR, 
                '.fc-next-button, [aria-label*="next"], .fc-icon-chevron-right, [class*="next"]')
            
            if next_button and next_button.is_enabled():
                # Click next month a few times to get to August
                for i in range(6):  # Navigate forward to get to August
                    next_button.click()
                    time.sleep(1)
                    current_view = self._get_current_month_year()
                    logger.info(f"   Navigated to: {current_view}")
                    
                    if self.target_month in current_view and self.target_year in current_view:
                        logger.info(f"✅ Successfully navigated to {self.target_month} {self.target_year}")
                        return True
                
                logger.warning("Could not reach August after navigation attempts")
                return False
            
            return False
            
        except Exception as e:
            logger.warning(f"Error navigating to August: {str(e)}")
            return False
    
    def _extract_month_events(self, calendar_type: str) -> List[Dict]:
        """Extract events from the current month view"""
        try:
            events = []
            seen_events = set()  # Track seen events to prevent duplicates
            
            # Find all event elements
            event_elements = self.browser.find_elements(By.CSS_SELECTOR, '.fc-event, a[href*="/event/"], [class*="event"]')
        
            for element in event_elements:
                try:
                    event = self._extract_event_from_element(element, calendar_type)
                    if event:
                        # Create a unique key for deduplication
                        event_key = f"{event['title']}_{event['date']}_{event['time']}"
                        
                        if event_key not in seen_events:
                            events.append(event)
                            seen_events.add(event_key)
                            logger.info(f"✅ Added event: {event['title']} on {event['date']} at {event['time']}")
                        else:
                            logger.info(f"🔄 Skipped duplicate: {event['title']} on {event['date']} at {event['time']}")
                    
                except Exception as e:
                    logger.warning(f"Error extracting event: {str(e)}")
                    continue
        
            logger.info(f"🎯 Extracted {len(events)} unique events (skipped {len(event_elements) - len(events)} duplicates)")
            return events
            
        except Exception as e:
            logger.error(f"Error extracting month events: {str(e)}")
            return []
    
    def _extract_event_from_element(self, element, calendar_type: str) -> Optional[Dict]:
        """Extract event data from a single element"""
        try:
            # Get the raw text first for debugging
            raw_text = element.text.strip()
            logger.debug(f"🔍 Raw element text: '{raw_text}'")
            
            # Get event title and clean it
            event_title = self._extract_clean_title(element)
            if not event_title or len(event_title) < 3:
                logger.debug(f"⚠️ Skipping element - title too short or empty: '{event_title}'")
=======
            # Parse the time from the event text (e.g., "10:30a Early Morning Prayer")
            time_str = ""
            if '\n' in title:
                time_part, event_title = title.split('\n', 1)
                time_str = time_part.strip()
                title = event_title.strip()
            else:
                # Try to extract time from the beginning of the text
                parts = title.split()
                if parts and any(char in parts[0].lower() for char in ['a', 'p', ':']):
                    time_str = parts[0]
                    title = ' '.join(parts[1:])
            
            # Try to find the actual date for this event
            date_str = None
            
            # First try: Look for data-date attribute in ancestor cells
            try:
                date_cell = event_element.find_element(By.XPATH, './ancestor::td[@data-date]')
                if date_cell:
                    date_str = date_cell.get_attribute('data-date')
                    logger.debug(f"Found date from ancestor cell: {date_str}")
            except:
                pass
            
            # Second try: Look for date in parent elements
            if not date_str:
                try:
                    parent_elements = event_element.find_elements(By.XPATH, './ancestor::*')
                    for parent in parent_elements:
                        try:
                            parent_date = parent.get_attribute('data-date')
                            if parent_date and len(parent_date) == 10:  # YYYY-MM-DD format
                                date_str = parent_date
                                logger.debug(f"Found date from parent element: {date_str}")
                                break
                        except:
                            continue
                except:
                    pass
            
            # Third try: Use the current month/year context as fallback
            if not date_str:
                try:
                    # Parse month name to number
                    month_num = datetime.strptime(month, '%B').month
                    year_num = int(year)
                    # Use the first day of the month as a fallback
                    date_str = f"{year_num}-{month_num:02d}-01"
                    logger.warning(f"Using fallback date for event '{title}': {date_str}")
                except:
                    # Use current date as fallback
                    date_str = datetime.now().strftime('%Y-%m-%d')
                    logger.warning(f"Using current date as fallback for event '{title}': {date_str}")
            
            if not date_str:
                logger.warning(f"Could not determine date for event: {title}")
>>>>>>> parent of b1d1c9c (stuf)
                return None
            
            # Get event date from the element or its parent
            date_str = self._extract_date_from_element(element)
            if not date_str:
                logger.debug(f"⚠️ Skipping element - no date found")
                return None
            
            # Get event time (separate from title)
            time_str = self._extract_time_from_element(element)
            
            # Parse the date and time
            event_date = datetime.strptime(date_str, '%Y-%m-%d')
            start_time, end_time = self._parse_time_with_offset(time_str, event_date)
            
            # Create event object
            event = {
                'title': title,
                'start': start_time,
                'end': end_time,
                'date': date_str,
                'time': time_str,
                'calendar_type': calendar_type,
                'url': f"https://antiochboone.com/calendar-{calendar_type}",
                'all_day': False,  # All events are timed events
                'source': 'Subsplash',
                'location': 'Antioch Boone',
                'unique_id': f"{calendar_type}_{date_str}_{title.lower().replace(' ', '_')}"
            }
            
<<<<<<< HEAD
            logger.info(f"✅ Extracted event: '{event_title}' on {date_str} at {time_str} → {start_time.strftime('%I:%M %p %Z')}")
            logger.debug(f"   Raw text: '{raw_text}'")
            logger.debug(f"   Clean title: '{event_title}'")
            logger.debug(f"   Extracted time: '{time_str}'")
            logger.debug(f"   Parsed start (Eastern): {start_time.strftime('%Y-%m-%d %I:%M %p %Z')}")
            logger.debug(f"   Parsed end (Eastern): {end_time.strftime('%Y-%m-%d %I:%M %p %Z')}")
            
=======
            logger.info(f"✅ Extracted event: '{title}' on {date_str} at {time_str}")
>>>>>>> parent of b1d1c9c (stuf)
            return event
            
        except Exception as e:
            logger.warning(f"Error extracting event from element: {str(e)}")
            return None
    
    def _extract_clean_title(self, element) -> str:
        """Extract clean event title without time information"""
        try:
<<<<<<< HEAD
            # Get the full text from the element
            full_text = element.text.strip()
            if not full_text:
                return ""
            
            # Remove time patterns from the title
            import re
            
            # Time patterns to remove (more comprehensive)
            time_patterns = [
                r'\b\d{1,2}:\d{2}[ap]?m?\b',  # 6:30a, 5:15pm
                r'\b\d{1,2}[ap]m\b',          # 6am, 5pm
                r'\b\d{1,2}:\d{2}\b',         # 14:30
                r'\d{1,2}:\d{2}[ap]?m?\s+\d{1,2}:\d{2}[ap]?m?',  # 6:30am 10:30a
                r'\b\d{1,2}:\d{2}[ap]?m?\s+\d{1,2}:\d{2}[ap]?m?\b',  # 6:30am 10:30a (word boundaries)
                r'\b\d{1,2}:\d{2}\s+\d{1,2}:\d{2}\b',  # 6:30 10:30
                r'\b\d{1,2}:\d{2}[ap]?m?\s+\d{1,2}:\d{2}[ap]?m?\s+',  # 6:30am 10:30a followed by space
            ]
            
            # Remove all time patterns
            clean_title = full_text
            for pattern in time_patterns:
                clean_title = re.sub(pattern, '', clean_title, flags=re.IGNORECASE)
            
            # Clean up extra whitespace and common artifacts
            clean_title = re.sub(r'\s+', ' ', clean_title)  # Multiple spaces to single
            clean_title = clean_title.strip()
            
            # Remove leading/trailing punctuation and numbers
            clean_title = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', clean_title)
            clean_title = re.sub(r'^\d+\s*', '', clean_title)  # Remove leading numbers
            
            # Additional cleanup for common artifacts
            clean_title = re.sub(r'^\s*[ap]m?\s*', '', clean_title, flags=re.IGNORECASE)  # Remove leading am/pm
            clean_title = re.sub(r'\s*[ap]m?\s*$', '', clean_title, flags=re.IGNORECASE)  # Remove trailing am/pm
            
            return clean_title
            
        except Exception as e:
            logger.warning(f"Error extracting clean title: {str(e)}")
            return element.text.strip() if element.text else ""
    
    def _extract_time_from_element(self, element) -> str:
        """Extract time from event element (separate from title)"""
        try:
            # Look for time in the element text
            text = element.text.strip()
            
            # Common time patterns
            time_patterns = [
                r'\b\d{1,2}:\d{2}[ap]?m?\b',  # 6:30a, 5:15pm
                r'\b\d{1,2}[ap]m\b',          # 6am, 5pm
                r'\b\d{1,2}:\d{2}\b'          # 14:30
            ]
            
            import re
            
            # Find all time patterns in the text
            all_times = []
            for pattern in time_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                all_times.extend(matches)
            
            if all_times:
                # If we found multiple times, be smarter about which one to use
                if len(all_times) > 1:
                    # Look for the most likely correct time
                    # Prefer times that look like actual event times (not 10:30, 9:15, etc.)
                    preferred_times = []
                    for time_str in all_times:
                        time_lower = time_str.lower()
                        # Prefer times that are likely actual event times
                        if any(pattern in time_lower for pattern in ['6:30', '5:15', '7:00', '8:00', '9:00']):
                            preferred_times.append(time_str)
                    
                    if preferred_times:
                        # Use the first preferred time
                        logger.info(f"Multiple times found in '{text}': {all_times}, using preferred: {preferred_times[0]}")
                        return preferred_times[0]
                    else:
                        # If no preferred times, use the first one but log a warning
                        logger.warning(f"Multiple times found, using first: {all_times[0]} from text: {text}")
                        return all_times[0]
                else:
                    # Only one time found, use it
                    return all_times[0]
            
            # No time found, return empty string to trigger default time
            return ""
            
        except Exception as e:
            logger.warning(f"Could not extract time: {str(e)}")
            return ""
    
    def _extract_date_from_element(self, element) -> Optional[str]:
        """Extract date from event element"""
        try:
            # Try to get date from data attributes
            date_attr = element.get_attribute('data-date')
            if date_attr:
                return date_attr
            
            # Try to get date from parent elements
            parent = element.find_element(By.XPATH, './..')
            date_attr = parent.get_attribute('data-date')
            if date_attr:
                return date_attr
            
            # Try to get date from the calendar day cell
            day_cell = element.find_element(By.XPATH, './ancestor::td[@data-date]')
            if day_cell:
                return day_cell.get_attribute('data-date')
            
            # Fallback: use current date
            return datetime.now().strftime('%Y-%m-%d')
            
        except Exception as e:
            logger.warning(f"Could not extract date: {str(e)}")
            return datetime.now().strftime('%Y-%m-%d')
    
    def _parse_time_with_offset(self, time_str: str, event_date: datetime) -> Tuple[datetime, datetime]:
        """Parse time and convert to Eastern Time using proper timezone conversion"""
        try:
            if not time_str or time_str.lower() in ['', 'invalid', 'error', 'all day', 'all-day']:
                # No valid time specified, use a default time (9:00 AM)
                logger.warning(f"No valid time found for '{time_str}', using default 9:00 AM")
                eastern_tz = pytz.timezone('America/New_York')
                start_time = eastern_tz.localize(event_date.replace(hour=9, minute=0, second=0, microsecond=0))
                end_time = start_time + timedelta(hours=1)
=======
            if not time_str:
                # No time specified, treat as all-day event
                start_time = event_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(days=1)
>>>>>>> parent of b1d1c9c (stuf)
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
<<<<<<< HEAD
            # If neither AM nor PM specified, assume 24-hour format
            
            # Validate hour and minute
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                logger.warning(f"Invalid time values: hour={hour}, minute={minute}, using default 9:00 AM")
                # Fallback to default time instead of all-day
                eastern_tz = pytz.timezone('America/New_York')
                start_time = eastern_tz.localize(event_date.replace(hour=9, minute=0, second=0, microsecond=0))
                end_time = start_time + timedelta(hours=1)
                return start_time, end_time
=======
                minute = int(time_str.split(':')[1])
            else:
                # 24-hour format
                hour, minute = map(int, time_str.split(':'))
>>>>>>> parent of b1d1c9c (stuf)
            
            # Create start time in local timezone (assume Eastern Time)
            # The website times are already in Eastern Time, so we just need to make them timezone-aware
            eastern_tz = pytz.timezone('America/New_York')
            start_time = eastern_tz.localize(event_date.replace(hour=hour, minute=minute, second=0, microsecond=0))
            
<<<<<<< HEAD
            # Default duration: 1 hour for most events
            end_time = start_time + timedelta(hours=1)
            
            logger.debug(f"🕐 Parsed time: {time_str} → {start_time.strftime('%I:%M %p %Z')}")
=======
            # Default duration: 1 hour
            end_time = start_time + timedelta(hours=1)
>>>>>>> parent of b1d1c9c (stuf)
            
            return start_time, end_time
            
        except Exception as e:
            logger.warning(f"Error parsing time '{time_str}': {str(e)}, using default 9:00 AM")
            # Fallback: use default time instead of all-day
            eastern_tz = pytz.timezone('America/New_York')
            start_time = eastern_tz.localize(event_date.replace(hour=9, minute=0, second=0, microsecond=0))
            end_time = start_time + timedelta(hours=1)
            return start_time, end_time
    
    # Removed old timezone offset methods - now using proper timezone conversion with pytz
    
    # All events are now timed events - no more all-day events
    
    def _navigate_to_next_month(self) -> bool:
        """Navigate to the next month in the calendar"""
        try:
            # Look for next month button
            next_button = self.browser.find_element(By.CSS_SELECTOR, '.fc-next-button, [aria-label*="next"], .fc-icon-chevron-right')
            if next_button and next_button.is_enabled():
                next_button.click()
                return True
            return False
<<<<<<< HEAD
        except Exception as e:
            logger.warning(f"Could not navigate to next month: {str(e)}")
            return False
=======
        
        return (start_time.hour == 0 and start_time.minute == 0 and 
                end_time.hour == 0 and end_time.minute == 0)
    
    def scrape_calendar_events(self, calendar_type: str) -> List[Dict]:
        """Scrape events from a specific calendar type for multiple months"""
        all_events = []
        empty_month_count = 0
        
        try:
            if not self.setup_browser():
                return all_events
            
            # Navigate to the calendar page
            calendar_url = self.calendar_urls.get(calendar_type)
            if not calendar_url:
                logger.error(f"No URL found for calendar type: {calendar_type}")
                return all_events
            
            logger.info(f"Navigating to {calendar_type} calendar: {calendar_url}")
            self.browser.get(calendar_url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Start with current month
            current_month, current_year = self.get_current_month_year()
            logger.info(f"Starting with current month: {current_month} {current_year}")
            
            # Scrape current month
            current_events = self.scrape_current_month_events(calendar_type)
            all_events.extend(current_events)
            logger.info(f"Collected {len(current_events)} events from {current_month}")
            
            if not current_events:
                empty_month_count += 1
            
            # Navigate through additional months
            for month_num in range(1, self.max_months_to_check):
                logger.info(f"Navigating to month {month_num + 1}...")
                
                # Navigate to next month
                if not self.navigate_to_next_month():
                    logger.error(f"Failed to navigate to month {month_num + 1}")
                    break
                
                # Verify we're on the right month
                actual_month, actual_year = self.get_current_month_year()
                logger.info(f"Calendar shows: {actual_month} {actual_year}")
                
                # Scrape this month's events
                month_events = self.scrape_current_month_events(calendar_type)
                all_events.extend(month_events)
                logger.info(f"Collected {len(month_events)} events from {actual_month}")
                
                if not month_events:
                    empty_month_count += 1
                    if empty_month_count >= self.max_consecutive_empty_months:
                        logger.info(f"Reached {self.max_consecutive_empty_months} consecutive empty months, stopping")
                        break
                else:
                    empty_month_count = 0  # Reset counter
                
                # Small delay between months
                time.sleep(2)
            
            return all_events
            
        except Exception as e:
            logger.error(f"Error scraping {calendar_type} calendar: {str(e)}")
            return all_events
        finally:
            if self.browser:
                self.browser.quit()
>>>>>>> parent of b1d1c9c (stuf)
    
    def sync_events_to_google(self, events: List[Dict], calendar_type: str) -> bool:
        """Sync events to Google Calendar"""
        try:
            if not self.google_service:
                logger.error("Google Calendar service not initialized")
                return False
            
            calendar_id = self.calendar_ids.get(calendar_type)
            if not calendar_id:
                logger.error(f"No Google Calendar ID found for {calendar_type}")
                return False
            
            logger.info(f"🔄 Syncing {len(events)} events to {calendar_type} Google Calendar")
            
            synced_count = 0
            for event in events:
                try:
                    if self._create_or_update_google_event(event, calendar_id):
                        synced_count += 1
                except Exception as e:
                    logger.warning(f"Failed to sync event '{event.get('title', 'Unknown')}': {str(e)}")
                    continue
            
            logger.info(f"✅ Successfully synced {synced_count}/{len(events)} events to {calendar_type} calendar")
            return synced_count > 0
            
        except Exception as e:
            logger.error(f"❌ Error syncing events to Google Calendar: {str(e)}")
            return False
    
    def _create_or_update_google_event(self, event: Dict, calendar_id: str) -> bool:
        """Create or update a Google Calendar event"""
        try:
            # Check if event already exists
            existing_event = self._find_existing_event(event, calendar_id)
            
            if existing_event:
                # Update existing event
                event_id = existing_event['id']
                updated_event = self.google_service.events().update(
                    calendarId=calendar_id,
                    eventId=event_id,
                    body=self._format_google_event(event)
                ).execute()
                logger.info(f"🔄 Updated event: {event['title']}")
                return True
            else:
                # Create new event
                new_event = self.google_service.events().insert(
                    calendarId=calendar_id,
                    body=self._format_google_event(event)
                ).execute()
                logger.info(f"✅ Created event: {event['title']}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating/updating Google Calendar event: {str(e)}")
            return False
    
    def _find_existing_event(self, event: Dict, calendar_id: str) -> Optional[Dict]:
        """Find existing event in Google Calendar"""
        try:
            # Search for events with similar title and date
            start_time = event['start'].isoformat() + 'Z'
            end_time = event['end'].isoformat() + 'Z'
            
            events_result = self.google_service.events().list(
                calendarId=calendar_id,
                timeMin=start_time,
                timeMax=end_time,
                q=event['title'],
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events_list = events_result.get('items', [])
            
            # Find exact match
            for existing_event in events_list:
                if (existing_event['summary'] == event['title'] and
                    existing_event['start'].get('dateTime', '').startswith(event['start'].strftime('%Y-%m-%d'))):
                    return existing_event
            
            return None
            
        except Exception as e:
            logger.warning(f"Error finding existing event: {str(e)}")
            return None
    
    def _format_google_event(self, event: Dict) -> Dict:
        """Format event for Google Calendar API"""
        google_event = {
            'summary': event['title'],
            'location': event.get('location', 'Antioch Boone'),
            'description': f"Source: {event.get('source', 'Subsplash')}\nURL: {event.get('url', '')}",
            'start': {},
            'end': {},
            'source': {
                'title': 'Subsplash Calendar Sync',
                'url': event.get('url', '')
            }
        }
        
        if event.get('all_day', False):
            google_event['start']['date'] = event['start'].strftime('%Y-%m-%d')
            google_event['end']['date'] = event['end'].strftime('%Y-%m-%d')
        else:
            # For timed events, we need to convert to the correct timezone
            # The event times are already corrected for the timezone offset
            # We just need to ensure Google Calendar knows the timezone
            google_event['start']['dateTime'] = event['start'].isoformat()
            google_event['end']['dateTime'] = event['end'].isoformat()
            google_event['start']['timeZone'] = 'America/New_York'
            google_event['end']['timeZone'] = 'America/New_York'
        
        return google_event
    
    def run_sync(self):
        """Main sync process"""
        try:
            if self.test_mode:
                logger.info("🧪 Starting TEST MODE Subsplash Calendar Sync")
                logger.info(f"🎯 Target: {self.target_month} {self.target_year} - Prayer Calendar Only")
            else:
                logger.info("🚀 Starting Production Subsplash Calendar Sync")
            
            # Setup browser
            if not self.setup_browser():
                logger.error("Failed to setup browser")
                return False
            
            # Authenticate with Google
            if not self.authenticate_google():
                logger.error("Failed to authenticate with Google")
                return False
            
            # Process each calendar type
            for calendar_type in self.calendar_ids.keys():
                if not self.calendar_ids[calendar_type]:
                    logger.info(f"Skipping {calendar_type} - no calendar ID configured")
                    continue
                
                try:
                    logger.info(f"📅 Processing {calendar_type} calendar...")
                    
                    # Scrape events
                    events = self.scrape_calendar_events(calendar_type)
                    
                    if events:
                        # Sync to Google Calendar
<<<<<<< HEAD
                        self.sync_events_to_google(events, calendar_type)
=======
                        sync_result = self.sync_events_to_google_calendar(events, calendar_type)
                        sync_results['calendar_results'][calendar_type] = sync_result
                        sync_results['total_events_processed'] += len(events)
                        
                        if sync_result['success']:
                            sync_results['calendars_processed'] += 1
                            logger.info(f"Successfully synced {calendar_type}: {sync_result['created']} created, {sync_result['updated']} updated")
                        else:
                            logger.error(f"Failed to sync {calendar_type}: {sync_result.get('error', 'Unknown error')}")
>>>>>>> parent of b1d1c9c (stuf)
                    else:
                        logger.info(f"No events found for {calendar_type} calendar")
                
                except Exception as e:
                    logger.error(f"Error processing {calendar_type} calendar: {str(e)}")
                    continue
            
            if self.test_mode:
                logger.info("🧪 TEST MODE sync completed successfully")
            else:
                logger.info("🎉 Production sync completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Calendar sync failed: {str(e)}")
            return False
        
        finally:
            if self.browser:
                self.browser.quit()
                logger.info("Browser closed")

def main():
    """Main entry point"""
    sync = SubsplashCalendarSync()
    success = sync.run_sync()
    
    if success:
        if sync.test_mode:
            print("🧪 TEST MODE sync completed successfully")
        else:
            print("✅ Calendar sync completed successfully")
        exit(0)
    else:
        print("❌ Calendar sync failed")
        exit(1)

if __name__ == "__main__":
    main()