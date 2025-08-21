#!/usr/bin/env python3
"""
Production Subsplash to Google Calendar Sync Script
This script automatically scrapes events from Subsplash calendars and syncs them to Google Calendar
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SubsplashCalendarSync:
    """Main class for syncing Subsplash calendars to Google Calendar"""
    
    def __init__(self):
        self.browser = None
        self.google_service = None
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
        
        # Calendar URLs mapping
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
        self.max_months_to_check = int(os.getenv('MAX_MONTHS_TO_CHECK', '6'))
        self.max_consecutive_empty_months = int(os.getenv('MAX_CONSECUTIVE_EMPTY_MONTHS', '3'))
        self.browser_wait_time = int(os.getenv('BROWSER_WAIT_TIME', '10'))
        self.save_debug_files = os.getenv('SAVE_DEBUG_FILES', 'false').lower() == 'true'
        
        logger.info("Initialized Subsplash Calendar Sync")
    
    def setup_browser(self) -> bool:
        """Setup Chrome browser for web scraping"""
        try:
            chrome_options = Options()
            
            # Check if running in GitHub Actions
            is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
            
            if is_github_actions:
                # GitHub Actions: Enhanced headless settings
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--disable-web-security')
                chrome_options.add_argument('--disable-features=VizDisplayCompositor')
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                
                # Use ChromeDriverManager in GitHub Actions (more reliable than system Chrome)
                service = Service(ChromeDriverManager().install())
            else:
                # Local development: Standard settings
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
                
                # Use ChromeDriverManager locally
                service = Service(ChromeDriverManager().install())
            
            self.browser = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set page load timeout
            self.browser.set_page_load_timeout(30)
            self.browser.implicitly_wait(10)
            
            logger.info(f"Browser setup successful ({'GitHub Actions' if is_github_actions else 'Local'})")
            return True
            
        except Exception as e:
            logger.error(f"Browser setup failed: {str(e)}")
            
            # Additional debugging for GitHub Actions
            if is_github_actions:
                logger.error("GitHub Actions debugging info:")
                try:
                    import subprocess
                    result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
                    logger.error(f"Chrome version: {result.stdout}")
                except Exception as chrome_error:
                    logger.error(f"Chrome version check failed: {chrome_error}")
                
                try:
                    result = subprocess.run(['which', 'google-chrome'], capture_output=True, text=True)
                    logger.error(f"Chrome path: {result.stdout}")
                except Exception as path_error:
                    logger.error(f"Chrome path check failed: {path_error}")
            
            return False
    
    def setup_google_calendar(self) -> bool:
        """Setup Google Calendar API service using OAuth 2.0 or pre-authenticated token"""
        try:
            # Check if we have OAuth credentials
            credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
            if not os.path.exists(credentials_file):
                logger.error(f"Google credentials file not found: {credentials_file}")
                return False
            
            # Check if we're in GitHub Actions (headless environment)
            is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
            
            if is_github_actions:
                # GitHub Actions: Use pre-authenticated token
                logger.info("Running in GitHub Actions - using pre-authenticated token")
                from google.oauth2.credentials import Credentials
                
                # Load the pre-authenticated token
                token_file = 'token.pickle'
                if os.path.exists(token_file):
                    with open(token_file, 'rb') as token:
                        creds = pickle.load(token)
                    
                    # Build the service
                    self.google_service = build('calendar', 'v3', credentials=creds)
                    logger.info("✅ Google Calendar API setup successful (GitHub Actions)")
                    return True
                else:
                    logger.error("Pre-authenticated token not found for GitHub Actions")
                    return False
            else:
                # Local development: Use OAuth 2.0 flow
                logger.info("Running locally - using OAuth 2.0 flow")
                from google_auth_oauthlib.flow import InstalledAppFlow
                from google.auth.transport.requests import Request
                
                # OAuth 2.0 scopes
                SCOPES = ['https://www.googleapis.com/auth/calendar']
                
                # Check if we have a valid token
                token_file = 'token.pickle'
                creds = None
                
                if os.path.exists(token_file):
                    with open(token_file, 'rb') as token:
                        creds = pickle.load(token)
                
                # If no valid credentials available, let the user log in
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                        creds = flow.run_local_server(port=0)
                    
                    # Save the credentials for the next run
                    with open(token_file, 'wb') as token:
                        pickle.dump(creds, token)
                
                # Build the service
                self.google_service = build('calendar', 'v3', credentials=creds)
                logger.info("✅ Google Calendar API setup successful (OAuth 2.0)")
                return True
            
        except Exception as e:
            logger.error(f"❌ Google Calendar setup failed: {str(e)}")
            return False
    
    def get_current_month_year(self) -> Tuple[str, str]:
        """Get the current month and year displayed in the calendar"""
        try:
            month_year_element = self.browser.find_element(By.CLASS_NAME, "fc-toolbar-title")
            month_year_text = month_year_element.text.strip()
            
            parts = month_year_text.split()
            if len(parts) == 2:
                month = parts[0]
                year = parts[1]
                return month, year
            else:
                logger.warning(f"Unexpected month/year format: {month_year_text}")
                return "Unknown", "Unknown"
                
        except Exception as e:
            logger.error(f"Error getting current month/year: {str(e)}")
            return "Unknown", "Unknown"
    
    def navigate_to_next_month(self) -> bool:
        """Click the next month button to navigate forward"""
        try:
            next_button = self.browser.find_element(By.CLASS_NAME, "fc-next-button")
            next_button.click()
            
            # Wait for the calendar to update
            time.sleep(3)
            
            # Wait for new events to load
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "fc-event"))
            )
            
            logger.info("Successfully navigated to next month")
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to next month: {str(e)}")
            return False
    
    def scrape_current_month_events(self, calendar_type: str) -> List[Dict]:
        """Scrape events from the currently displayed month."""
        events = []
        
        if self.save_debug_files:
            # Save page source for debugging
            debug_file_path = f"debug_page_source_{calendar_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(debug_file_path, 'w', encoding='utf-8') as f:
                f.write(self.browser.page_source)
            logger.info(f"Saved debug page source to {debug_file_path}")

        # Wait for the calendar to fully load
        try:
            logger.info(f"Waiting for calendar container with timeout: {self.browser_wait_time}s")
            WebDriverWait(self.browser, self.browser_wait_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.fc-view-container'))
            )
            logger.info("✅ Calendar container found")
            # Additional wait for FullCalendar to render events
            logger.info("Waiting 3 seconds for FullCalendar to render events...")
            time.sleep(3)
            
            # Analyze the calendar structure to understand the layout
            self._analyze_calendar_structure(calendar_type)
            
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
            '.fc-event',   # Any FullCalendar event
            'a[href*="/event/"]',  # Event links
            '.fc-daygrid-event',   # Day grid events
            '.fc-event-harness a'  # Events within harness
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
                    
                    # Log details for debugging
                    for i, elem in enumerate(elements[:5]):
                        try:
                            title = elem.text.strip()[:100] if elem.text else "NO_TEXT"
                            classes = elem.get_attribute('class') or "NO_CLASS"
                            tag = elem.tag_name
                            
                            # Detailed debugging to find where real times are stored
                            logger.info(f"  Element {i}: Tag='{tag}' Class='{classes}' Text='{title}'")
                            
                            # Look for time-specific elements within this event
                            time_elements = elem.find_elements(By.CSS_SELECTOR, '.fc-event-time, .fc-event-title, [class*="time"], [class*="title"]')
                            logger.info(f"    Time-related sub-elements: {len(time_elements)}")
                            for j, time_elem in enumerate(time_elements):
                                try:
                                    time_text = time_elem.text.strip()[:50] if time_elem.text else "NO_TEXT"
                                    time_class = time_elem.get_attribute('class') or "NO_CLASS"
                                    logger.info(f"      Sub-element {j}: class='{time_class}' text='{time_text}'")
                                except Exception as sub_e:
                                    logger.info(f"      Sub-element {j}: Error getting info: {sub_e}")
                            
                            # Look for any data attributes that might contain time info
                            data_attrs = elem.get_attribute('outerHTML')[:500] if elem.get_attribute('outerHTML') else "NO_HTML"
                            logger.info(f"    HTML preview: {data_attrs}")
                            
                            # Look for data attributes that might contain real event info
                            event_id = elem.get_attribute('data-id') or "NO_ID"
                            href = elem.get_attribute('href') or "NO_HREF"
                            logger.info(f"    Event ID: {event_id}")
                            logger.info(f"    Event URL: {href}")
                            
                            # Check if there are any other data attributes
                            all_attrs = elem.get_attribute('outerHTML')
                            if all_attrs:
                                # Look for data-* attributes
                                import re
                                data_pattern = r'data-([^=]+)="([^"]*)"'
                                data_matches = re.findall(data_pattern, all_attrs)
                                if data_matches:
                                    logger.info(f"    Data attributes: {data_matches}")
                                else:
                                    logger.info(f"    No data attributes found")
                            
                            # Look for any hidden elements or spans that might contain real times
                            hidden_elements = elem.find_elements(By.CSS_SELECTOR, '[style*="display: none"], [hidden], [aria-hidden="true"]')
                            if hidden_elements:
                                logger.info(f"    Hidden elements: {len(hidden_elements)}")
                                for k, hidden_elem in enumerate(hidden_elements[:3]):
                                    try:
                                        hidden_text = hidden_elem.text.strip()[:50] if hidden_elem.text else "NO_TEXT"
                                        hidden_class = hidden_elem.get_attribute('class') or "NO_CLASS"
                                        logger.info(f"      Hidden {k}: class='{hidden_class}' text='{hidden_text}'")
                                    except Exception as hidden_e:
                                        logger.info(f"      Hidden {k}: Error getting info: {hidden_e}")
                            else:
                                logger.info(f"    No hidden elements found")
                        except Exception as debug_e:
                            logger.info(f"  Element {i}: Error getting info: {debug_e}")
                    
                    break
                else:
                    logger.info(f"  ⚠️  No elements found with selector '{selector}'")
            except Exception as e:
                logger.warning(f"  ❌ Selector '{selector}' failed: {e}")
                continue
        
        # If no events found, log what we did find for debugging
        if not event_elements:
            logger.warning("No FullCalendar events found with working selector")
            # Log what we did find for debugging
            try:
                all_divs = self.browser.find_elements(By.TAG_NAME, 'div')
                event_like_divs = [div for div in all_divs if any(keyword in div.get_attribute('class') or keyword in div.get_attribute('id') or keyword in div.text.lower() 
                                                               for keyword in ['event', 'calendar', 'schedule', 'meeting', 'prayer', 'kids', 'bam'])]
                logger.info(f"Found {len(event_like_divs)} divs that might contain event info")
                
                # Save a sample for debugging
                if event_like_divs and self.save_debug_files:
                    debug_elements = []
                    for i, div in enumerate(event_like_divs[:10]):
                        try:
                            debug_elements.append({
                                'index': i,
                                'class': div.get_attribute('class'),
                                'id': div.get_attribute('id'),
                                'text': div.text[:200] if div.text else '',
                                'tag': div.tag_name
                            })
                        except:
                            continue
                    
                    debug_file_path = f"debug_elements_{calendar_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(debug_file_path, 'w', encoding='utf-8') as f:
                        json.dump(debug_elements, f, indent=2)
                    logger.info(f"Saved debug elements to {debug_file_path}")
                
            except Exception as e:
                logger.debug(f"Error analyzing page structure: {e}")
            
            return []

        # Extract events using the found selector
        current_month_year = self.get_current_month_year()
        if not current_month_year:
            logger.warning("Could not determine current month/year for scraping.")
            return []

        # Deduplicate elements to prevent multiple copies of the same event
        unique_elements = self._deduplicate_event_elements(event_elements)
        logger.info(f"Found {len(event_elements)} total elements, deduplicated to {len(unique_elements)} unique elements")

        for element in unique_elements:
            try:
                month, year = current_month_year
                event_data = self._extract_fc_event(element, month, year, calendar_type)
                if event_data:
                    events.append(event_data)
                    logger.debug(f"Extracted event: {event_data['title']} on {event_data['date']}")
            except Exception as e:
                logger.warning(f"Error extracting event from element: {e}")
                continue

        if events:
            logger.info(f"Successfully extracted {len(events)} events using {used_selector}")
        else:
            logger.warning(f"Found {len(event_elements)} elements with {used_selector} but failed to extract event data")
            
            # Debug: Try to see what's in these elements
            if self.save_debug_files and event_elements:
                debug_events = []
                for i, element in enumerate(event_elements[:5]):  # First 5
                    try:
                        debug_events.append({
                            'index': i,
                            'tag': element.tag_name,
                            'class': element.get_attribute('class'),
                            'text': element.text[:200] if element.text else '',
                            'html': element.get_attribute('outerHTML')[:500] if element.get_attribute('outerHTML') else ''
                        })
                    except:
                        continue
                
                debug_file_path = f"debug_event_elements_{calendar_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(debug_file_path, 'w', encoding='utf-8') as f:
                    json.dump(debug_events, f, indent=2)
                logger.info(f"Saved debug event elements to {debug_file_path}")

        return events
    
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
                
                # Clean the title for comparison (remove time prefix)
                clean_title = title
                if '\n' in title:
                    parts = title.split('\n')
                    if len(parts) >= 2:
                        clean_title = parts[1].strip()
                else:
                    # Try to extract title without time
                    parts = title.split()
                    if parts and any(char in parts[0].lower() for char in ['a', 'p', ':']):
                        clean_title = ' '.join(parts[1:])
                
                # Simple deduplication: if we've seen this clean title before, skip it
                if clean_title not in seen_titles:
                    seen_titles.add(clean_title)
                    unique_elements.append(element)
                    logger.debug(f"Added unique event: {clean_title}")
                else:
                    logger.debug(f"Skipped duplicate event: {clean_title}")
                    
            except Exception as e:
                logger.debug(f"Error during deduplication: {e}")
                continue
        
        logger.info(f"Deduplication: {len(event_elements)} total elements -> {len(unique_elements)} unique elements")
        return unique_elements
    
    def _extract_fc_event(self, event_element, month: str, year: str, calendar_type: str) -> Optional[Dict]:
        """Extract event data from a FullCalendar event element"""
        try:
            # Get the text content directly from the element
            title = event_element.text.strip()
            if not title or len(title) < 3:
                return None
            
            # Extract time from the separate fc-event-time element (this is the correct way for FullCalendar)
            time_str = ""
            event_title = title
            
            try:
                # Look for the time element within this event
                time_element = event_element.find_element(By.CSS_SELECTOR, '.fc-event-time')
                if time_element:
                    time_str = time_element.text.strip()
                    logger.debug(f"Found time from fc-event-time element: {time_str}")
                    
                    # Extract the title from the fc-event-title element
                    title_element = event_element.find_element(By.CSS_SELECTOR, '.fc-event-title')
                    if title_element:
                        event_title = title_element.text.strip()
                        logger.debug(f"Found title from fc-event-title element: {event_title}")
                else:
                    # Fallback: Parse the time from the event text (e.g., "10:30a Early Morning Prayer" or "6:30a\nEarly Morning Prayer")
                    if '\n' in title:
                        parts = title.split('\n')
                        if len(parts) >= 2:
                            time_str = parts[0].strip()
                            event_title = parts[1].strip()
                        else:
                            # Fallback: try to extract time from beginning
                            parts = title.split()
                            if parts and any(char in parts[0].lower() for char in ['a', 'p', ':']):
                                time_str = parts[0]
                                event_title = ' '.join(parts[1:])
                    else:
                        # Try to extract time from the beginning of the text
                        parts = title.split()
                        if parts and any(char in parts[0].lower() for char in ['a', 'p', ':']):
                            time_str = parts[0]
                            event_title = ' '.join(parts[1:])
            except Exception as e:
                logger.debug(f"Could not find time/title elements, using fallback parsing: {e}")
                # Fallback: Parse the time from the event text
                if '\n' in title:
                    parts = title.split('\n')
                    if len(parts) >= 2:
                        time_str = parts[0].strip()
                        event_title = parts[1].strip()
                    else:
                        parts = title.split()
                        if parts and any(char in parts[0].lower() for char in ['a', 'p', ':']):
                            time_str = parts[0]
                            event_title = ' '.join(parts[1:])
                else:
                    parts = title.split()
                    if parts and any(char in parts[0].lower() for char in ['a', 'p', ':']):
                        time_str = parts[0]
                        event_title = ' '.join(parts[1:])
            
            # Try to find the actual date for this event using FullCalendar structure
            date_str = None
            
            # First try: Look for the day cell that contains this event
            try:
                # Find the parent day cell using FullCalendar's structure
                day_cell = event_element.find_element(By.XPATH, './ancestor::td[contains(@class, "fc-daygrid-day")]')
                if day_cell:
                    # Look for data-date attribute first
                    cell_date = day_cell.get_attribute('data-date')
                    if cell_date:
                        date_str = cell_date
                        logger.info(f"✅ Found date from day cell data-date: {date_str}")
                    else:
                        # Try to get date from the day number text
                        day_number_elem = day_cell.find_element(By.CSS_SELECTOR, '.fc-daygrid-day-number')
                        if day_number_elem:
                            day_text = day_number_elem.text.strip()
                            if day_text and day_text.isdigit():
                                day_num = int(day_text)
                                # Parse month name to number
                                month_num = datetime.strptime(month, '%B').month
                                year_num = int(year)
                                date_str = f"{year_num}-{month_num:02d}-{day_num:02d}"
                                logger.info(f"✅ Constructed date from day number: {date_str}")
                            else:
                                logger.warning(f"Day number text is not a digit: '{day_text}'")
                        else:
                            logger.warning("Could not find day number element")
                else:
                    logger.warning("Could not find day cell")
            except Exception as e:
                logger.warning(f"Error finding day cell: {e}")
                pass
            
            # Second try: Look for data-date attribute in ancestor cells
            if not date_str:
                try:
                    date_cell = event_element.find_element(By.XPATH, './ancestor::td[@data-date]')
                    if date_cell:
                        date_str = date_cell.get_attribute('data-date')
                        logger.debug(f"Found date from ancestor cell: {date_str}")
                except:
                    pass
            
            # Third try: Look for date in parent elements
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
            
            # Fourth try: Use the current month/year context as fallback
            if not date_str:
                try:
                    # Parse month name to number
                    month_num = datetime.strptime(month, '%B').month
                    year_num = int(year)
                    # Use the first day of the month as a fallback
                    date_str = f"{year_num}-{month_num:02d}-01"
                    logger.warning(f"Using fallback date for event '{event_title}': {date_str}")
                except:
                    # Use current date as fallback
                    date_str = datetime.now().strftime('%Y-%m-%d')
                    logger.warning(f"Using current date as fallback for event '{event_title}': {date_str}")
            
            if not date_str:
                logger.warning(f"Could not determine date for event: {event_title}")
                return None
            
            # Parse the date
            try:
                event_date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                logger.warning(f"Could not parse date: {date_str}")
                return None
            
            # Parse the time and create start/end times
            start_time, end_time = self._parse_fc_time(time_str, event_date)
            
            # Create event object
            event = {
                'title': event_title,
                'start': start_time,
                'end': end_time,
                'date': date_str,
                'time': time_str,
                'month': month,
                'year': year,
                'calendar_type': calendar_type,
                'url': f"https://antiochboone.com/calendar-{calendar_type}",
                'all_day': self._is_all_day_event(start_time, end_time),
                'source': 'Subsplash',
                'location': 'Antioch Boone',
                'unique_id': f"{calendar_type}_{date_str}_{event_title.lower().replace(' ', '_')}"
            }
            
            logger.info(f"✅ Extracted event: '{event_title}' on {date_str} at {time_str}")
            return event
            
        except Exception as e:
            logger.warning(f"Error extracting event from element: {str(e)}")
            return None
    
    def _parse_fc_time(self, time_str: str, event_date: datetime) -> Tuple[datetime, datetime]:
        """Parse FullCalendar time format and return start/end times"""
        try:
            if not time_str or time_str.lower() in ['all day', 'all-day', '']:
                # No time specified, treat as all-day event
                start_time = event_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(days=1)
                return start_time, end_time
            
            # Parse time formats like "6:30a", "5:15p", "10:00", "6:30am", "5:15pm"
            time_str = time_str.lower().strip()
            
            # Handle AM/PM variations
            is_am = False
            is_pm = False
            
            if 'a' in time_str and 'm' not in time_str:
                # Handle "6:30a" format
                time_str = time_str.replace('a', '').strip()
                is_am = True
            elif 'am' in time_str:
                # Handle "6:30am" format
                time_str = time_str.replace('am', '').strip()
                is_am = True
            elif 'p' in time_str and 'm' not in time_str:
                # Handle "5:15p" format
                time_str = time_str.replace('p', '').strip()
                is_pm = True
            elif 'pm' in time_str:
                # Handle "5:15pm" format
                time_str = time_str.replace('pm', '').strip()
                is_pm = True
            
            # Parse hour and minute
            if ':' in time_str:
                hour, minute = map(int, time_str.split(':'))
            else:
                # Handle "6a" format (just hour)
                hour = int(time_str)
                minute = 0
            
            # Apply AM/PM logic
            if is_am:
                if hour == 12:
                    hour = 0
            elif is_pm:
                if hour != 12:
                    hour += 12
            # If neither AM nor PM specified, assume 24-hour format
            
            # Validate hour and minute
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                logger.warning(f"Invalid time values: hour={hour}, minute={minute}")
                # Fallback to all-day event
                start_time = event_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(days=1)
                return start_time, end_time
            
            # Create start time
            start_time = event_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Default duration: 1 hour for most events
            # Special handling for known event types
            if 'prayer' in event_date.strftime('%A').lower():  # If it's a prayer day
                if hour < 12:  # Morning prayer
                    end_time = start_time + timedelta(hours=1)
                else:  # Evening prayer
                    end_time = start_time + timedelta(hours=1)
            else:
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
        
        return (start_time.hour == 0 and start_time.minute == 0 and 
                end_time.hour == 0 and end_time.minute == 0)
    
    def _detect_weekly_recurring_events(self, events: List[Dict], calendar_type: str) -> List[Dict]:
        """Detect weekly recurring events and expand them for the next few months"""
        expanded_events = []
        
        # Known weekly recurring events based on your actual schedule
        weekly_patterns = {
            'Early Morning Prayer': {
                'time': '6:30a',
                'days': ['Thursday'],  # Thursdays only
                'duration_hours': 1,
                'frequency': 'weekly'
            },
            'Prayer Set': {
                'time': '5:15p',
                'days': ['Tuesday'],  # Tuesdays only
                'duration_hours': 1,
                'frequency': 'weekly'
            },
            'BAM': {
                'time': '7:15a',
                'days': [],  # No specific days - monthly only
                'duration_hours': 1,
                'frequency': 'monthly'
            }
        }
        
        # Group events by title to detect patterns
        event_groups = {}
        for event in events:
            event_title = event['title']
            if event_title not in event_groups:
                event_groups[event_title] = []
            event_groups[event_title].append(event)
        
        # Analyze each group for weekly patterns
        for event_title, event_list in event_groups.items():
            if len(event_list) < 2:
                # Single event, just add it
                expanded_events.extend(event_list)
                continue
            
            # Sort events by date
            event_list.sort(key=lambda x: x['date'])
            
            # Check if this matches a known weekly pattern
            if event_title in weekly_patterns:
                pattern = weekly_patterns[event_title]
                logger.info(f"Detected known weekly pattern for '{event_title}': {pattern['days']}")
                
                # Get the base date from the first event
                try:
                    base_date = datetime.strptime(event_list[0]['date'], '%Y-%m-%d')
                except:
                    expanded_events.extend(event_list)
                    continue
                
                # Expand for the next 3 months (12 weeks)
                for week in range(1, 13):
                    for day_name in pattern['days']:
                        # Calculate the next occurrence of this day
                        target_date = self._get_next_weekday(base_date, day_name, week)
                        
                        if target_date:
                            # Parse the time from the pattern
                            time_parts = pattern['time'].split(':')
                            hour = int(time_parts[0])
                            minute = int(time_parts[1].replace('a', '').replace('p', ''))
                            
                            # Create the recurring event
                            start_time = target_date.replace(
                                hour=hour,
                                minute=minute,
                                second=0, microsecond=0
                            )
                            
                            # Handle AM/PM
                            if 'a' in pattern['time']:
                                if start_time.hour == 12:
                                    start_time = start_time.replace(hour=0)
                            elif 'p' in pattern['time']:
                                if start_time.hour != 12:
                                    start_time = start_time.replace(hour=start_time.hour + 12)
                            
                            end_time = start_time + timedelta(hours=pattern['duration_hours'])
                            
                            recurring_event = {
                                'title': event_title,
                                'start': start_time,
                                'end': end_time,
                                'date': start_time.strftime('%Y-%m-%d'),
                                'time': pattern['time'],
                                'month': start_time.strftime('%B'),
                                'year': str(start_time.year),
                                'calendar_type': calendar_type,
                                'url': event_list[0]['url'],
                                'all_day': False,
                                'source': 'Subsplash',
                                'location': 'Antioch Boone',
                                'unique_id': f"{calendar_type}_{start_time.strftime('%Y-%m-%d')}_{event_title.lower().replace(' ', '_')}",
                                'recurring': True,
                                'pattern': f"Weekly on {', '.join(pattern['days'])}"
                            }
                            
                            expanded_events.append(recurring_event)
                            logger.info(f"✅ Added recurring event: {event_title} on {start_time.strftime('%Y-%m-%d')} at {pattern['time']}")
                
                # Also add the original scraped events
                expanded_events.extend(event_list)
                
            else:
                # Unknown pattern, just add the events as-is
                expanded_events.extend(event_list)
                logger.info(f"No known weekly pattern for '{event_title}', adding {len(event_list)} events as-is")
        
        logger.info(f"Expanded {len(events)} events to {len(expanded_events)} total events (including recurring)")
        return expanded_events
    
    def _get_next_weekday(self, base_date: datetime, target_day: str, weeks_ahead: int) -> Optional[datetime]:
        """Get the date of a specific weekday, weeks ahead from base date"""
        try:
            # Convert day name to number (Monday=0, Sunday=6)
            day_map = {
                'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
                'Friday': 4, 'Saturday': 5, 'Sunday': 6
            }
            
            target_day_num = day_map.get(target_day)
            if target_day_num is None:
                return None
            
            # Calculate days to add
            current_day = base_date.weekday()
            days_to_add = (target_day_num - current_day + 7) % 7 + (weeks_ahead * 7)
            
            target_date = base_date + timedelta(days=days_to_add)
            return target_date
            
        except Exception as e:
            logger.warning(f"Error calculating next weekday: {str(e)}")
            return None

    def _analyze_calendar_structure(self, calendar_type: str):
        """Analyze the calendar structure to understand how events are organized"""
        try:
            logger.info("🔍 Analyzing calendar structure...")
            
            # Look for the calendar grid
            calendar_grid = self.browser.find_elements(By.CSS_SELECTOR, '.fc-daygrid-body, .fc-view-container')
            logger.info(f"Found {len(calendar_grid)} calendar grid elements")
            
            # Look for day cells
            day_cells = self.browser.find_elements(By.CSS_SELECTOR, '.fc-day, .fc-daygrid-day, td[data-date]')
            logger.info(f"Found {len(day_cells)} day cells")
            
            # Analyze a few day cells to understand the structure
            for i, cell in enumerate(day_cells[:5]):
                try:
                    cell_date = cell.get_attribute('data-date')
                    cell_classes = cell.get_attribute('class')
                    cell_text = cell.text.strip()[:100] if cell.text else "NO_TEXT"
                    
                    logger.info(f"Day cell {i}: date='{cell_date}' classes='{cell_classes}' text='{cell_text}'")
                    
                    # Look for events within this cell
                    events_in_cell = cell.find_elements(By.CSS_SELECTOR, '.fc-event, a[href*="/event/"]')
                    logger.info(f"  Events in cell: {len(events_in_cell)}")
                    
                    for j, event in enumerate(events_in_cell[:3]):
                        try:
                            event_text = event.text.strip()[:50] if event.text else "NO_TEXT"
                            event_href = event.get_attribute('href') or "NO_HREF"
                            logger.info(f"    Event {j}: text='{event_text}' href='{event_href}'")
                        except:
                            logger.info(f"    Event {j}: Error getting info")
                            
                except Exception as e:
                    logger.info(f"Day cell {i}: Error analyzing: {e}")
            
            # Look for the month navigation
            month_elements = self.browser.find_elements(By.CSS_SELECTOR, '.fc-toolbar-title, [class*="month"], [class*="year"]')
            logger.info(f"Found {len(month_elements)} month/year elements")
            
            for i, elem in enumerate(month_elements[:3]):
                try:
                    elem_text = elem.text.strip()[:50] if elem.text else "NO_TEXT"
                    elem_class = elem.get_attribute('class') or "NO_CLASS"
                    logger.info(f"Month element {i}: class='{elem_class}' text='{elem_text}'")
                except:
                    logger.info(f"Month element {i}: Error getting info")
                    
        except Exception as e:
            logger.error(f"Error analyzing calendar structure: {e}")

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
    
    def sync_events_to_google_calendar(self, events: List[Dict], calendar_type: str) -> Dict:
        """Sync events to Google Calendar"""
        if not self.google_service:
            logger.error("Google Calendar service not initialized")
            return {'success': False, 'error': 'Google Calendar service not initialized'}
        
        calendar_id = self.calendar_ids.get(calendar_type)
        if not calendar_id:
            logger.error(f"No Google Calendar ID found for {calendar_type}")
            return {'success': False, 'error': f'No Google Calendar ID for {calendar_type}'}
        
        results = {
            'success': True,
            'calendar_type': calendar_type,
            'total_events': len(events),
            'created': 0,
            'updated': 0,
            'errors': 0,
            'error_details': []
        }
        
        for event in events:
            try:
                # Check if event already exists
                existing_event = self._find_existing_event(event, calendar_id)
                
                if existing_event:
                    # Update existing event
                    updated_event = self._update_google_calendar_event(
                        calendar_id, existing_event['id'], event
                    )
                    if updated_event:
                        results['updated'] += 1
                        logger.info(f"Updated event: {event['title']}")
                    else:
                        results['errors'] += 1
                        results['error_details'].append(f"Failed to update: {event['title']}")
                else:
                    # Create new event
                    created_event = self._create_google_calendar_event(calendar_id, event)
                    if created_event:
                        results['created'] += 1
                        logger.info(f"Created event: {event['title']}")
                    else:
                        results['errors'] += 1
                        results['error_details'].append(f"Failed to create: {event['title']}")
                
            except Exception as e:
                results['errors'] += 1
                error_msg = f"Error processing {event['title']}: {str(e)}"
                results['error_details'].append(error_msg)
                logger.error(error_msg)
        
        return results
    
    def _find_existing_event(self, event: Dict, calendar_id: str) -> Optional[Dict]:
        """Find existing event in Google Calendar"""
        try:
            # Search for events with similar title and time
            time_min = event['start'].isoformat() + 'Z'
            time_max = (event['start'] + timedelta(days=1)).isoformat() + 'Z'
            
            events_result = self.google_service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                q=event['title'],
                singleEvents=True
            ).execute()
            
            events_list = events_result.get('items', [])
            
            # Find exact match - improved logic
            for existing_event in events_list:
                if existing_event['summary'] == event['title']:
                    # Check if the event is on the same date
                    existing_start = existing_event['start'].get('dateTime', '')
                    if existing_start:
                        # Parse the existing event's date
                        try:
                            existing_date = existing_start.split('T')[0]  # Get just the date part
                            if existing_date == event['date']:
                                logger.debug(f"Found existing event: {event['title']} on {existing_date}")
                                return existing_event
                        except (IndexError, ValueError):
                            continue
            
            logger.debug(f"No existing event found for: {event['title']} on {event['date']}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding existing event: {str(e)}")
            return None
    
    def _create_google_calendar_event(self, calendar_id: str, event: Dict) -> Optional[Dict]:
        """Create new event in Google Calendar"""
        try:
            google_event = {
                'summary': event['title'],
                'location': event['location'],
                'description': f"Source: {event['source']}\nURL: {event['url']}\nUnique ID: {event['unique_id']}",
                'start': {
                    'dateTime': event['start'].isoformat(),
                    'timeZone': 'America/New_York',
                },
                'end': {
                    'dateTime': event['end'].isoformat(),
                    'timeZone': 'America/New_York',
                },
                'source': {
                    'title': 'Subsplash Calendar',
                    'url': event['url']
                }
            }
            
            created_event = self.google_service.events().insert(
                calendarId=calendar_id,
                body=google_event
            ).execute()
            
            return created_event
            
        except Exception as e:
            logger.error(f"Error creating Google Calendar event: {str(e)}")
            return None
    
    def _update_google_calendar_event(self, calendar_id: str, event_id: str, event: Dict) -> Optional[Dict]:
        """Update existing event in Google Calendar"""
        try:
            google_event = {
                'summary': event['title'],
                'location': event['location'],
                'description': f"Source: {event['source']}\nURL: {event['url']}\nUnique ID: {event['unique_id']}",
                'start': {
                    'dateTime': event['start'].isoformat(),
                    'timeZone': 'America/New_York',
                },
                'end': {
                    'dateTime': event['end'].isoformat(),
                    'timeZone': 'America/New_York',
                },
                'source': {
                    'title': 'Subsplash Calendar',
                    'url': event['url']
                }
            }
            
            updated_event = self.google_service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=google_event
            ).execute()
            
            return updated_event
            
        except Exception as e:
            logger.error(f"Error updating Google Calendar event: {str(e)}")
            return None
    
    def run_full_sync(self) -> Dict:
        """Run the full sync process for all calendars"""
        sync_results = {
            'timestamp': datetime.now().isoformat(),
            'overall_success': True,
            'calendars_processed': 0,
            'total_events_processed': 0,
            'calendar_results': {}
        }
        
        try:
            # Setup Google Calendar
            if not self.setup_google_calendar():
                sync_results['overall_success'] = False
                sync_results['error'] = 'Failed to setup Google Calendar'
                return sync_results
            
            # Only process calendars that have Google Calendar IDs configured
            configured_calendars = {
                calendar_type: calendar_id 
                for calendar_type, calendar_id in self.calendar_ids.items() 
                if calendar_id
            }
            
            logger.info(f"Found {len(configured_calendars)} configured calendars: {list(configured_calendars.keys())}")
            
            # Process each configured calendar type
            for calendar_type, calendar_id in configured_calendars.items():
                logger.info(f"Processing {calendar_type} calendar...")
                
                try:
                    # Scrape events
                    events = self.scrape_calendar_events(calendar_type)
                    logger.info(f"Found {len(events)} events for {calendar_type}")
                    
                    if events:
                        # Detect and expand recurring events
                        expanded_events = self._detect_weekly_recurring_events(events, calendar_type)
                        
                        # Sync to Google Calendar
                        sync_result = self.sync_events_to_google_calendar(expanded_events, calendar_type)
                        sync_results['calendar_results'][calendar_type] = sync_result
                        sync_results['total_events_processed'] += len(expanded_events)
                        
                        if sync_result['success']:
                            sync_results['calendars_processed'] += 1
                            logger.info(f"Successfully synced {calendar_type}: {sync_result['created']} created, {sync_result['updated']} updated")
                        else:
                            logger.error(f"Failed to sync {calendar_type}: {sync_result.get('error', 'Unknown error')}")
                    else:
                        logger.info(f"No events found for {calendar_type}")
                        sync_results['calendar_results'][calendar_type] = {
                            'success': True,
                            'total_events': 0,
                            'message': 'No events found'
                        }
                
                except Exception as e:
                    error_msg = f"Error processing {calendar_type}: {str(e)}"
                    logger.error(error_msg)
                    sync_results['calendar_results'][calendar_type] = {
                        'success': False,
                        'error': error_msg
                    }
            
            return sync_results
            
        except Exception as e:
            error_msg = f"Error during full sync: {str(e)}"
            logger.error(error_msg)
            sync_results['overall_success'] = False
            sync_results['error'] = error_msg
            return sync_results

def main():
    """Main function to run the calendar sync"""
    logger.info("🚀 Starting Subsplash Calendar Sync")
    
    # Create sync instance
    sync = SubsplashCalendarSync()
    
    # Run full sync
    results = sync.run_full_sync()
    
    # Display results
    print("\n" + "="*80)
    print("📊 SYNC RESULTS")
    print("="*80)
    
    if results['overall_success']:
        print(f"✅ Sync completed successfully!")
        print(f"📅 Calendars processed: {results['calendars_processed']}")
        print(f"📝 Total events processed: {results['total_events_processed']}")
        print()
        
        for calendar_type, result in results['calendar_results'].items():
            if result['success']:
                if 'total_events' in result:
                    print(f"📅 {calendar_type}: {result['total_events']} events")
                else:
                    print(f"📅 {calendar_type}: {result['created']} created, {result['updated']} updated")
            else:
                print(f"❌ {calendar_type}: {result.get('error', 'Unknown error')}")
    else:
        print(f"❌ Sync failed: {results.get('error', 'Unknown error')}")
    
    print("="*80)
    
    # Save results to file
    with open('sync_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("Results saved to sync_results.json")

if __name__ == "__main__":
    main()