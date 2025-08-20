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
                
                # Use system Chrome in GitHub Actions
                service = Service('/usr/bin/google-chrome')
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

        # Try multiple FullCalendar selectors in order of specificity
        event_selectors = [
            'a.fc-event',  # Most specific - FullCalendar event links
            '.fc-event',   # FullCalendar event elements
            'div.fc-event', # FullCalendar event divs
            '[class*="fc-event"]', # Any element with fc-event in class
        ]
        
        event_elements = []
        used_selector = None
        
        # First try: Standard FullCalendar selectors
        logger.info("🔍 STEP 1: Trying standard FullCalendar selectors...")
        for selector in event_selectors:
            try:
                logger.info(f"  Trying selector: '{selector}'")
                elements = self.browser.find_elements(By.CSS_SELECTOR, selector)
                logger.info(f"  Found {len(elements)} elements with selector '{selector}'")
                
                if elements:
                    event_elements = elements
                    used_selector = selector
                    logger.info(f"✅ SUCCESS: Found {len(elements)} events using selector: {selector}")
                    
                    # Additional debugging for GitHub Actions
                    if os.getenv('GITHUB_ACTIONS') == 'true':
                        logger.info(f"🔍 GitHub Actions: Detailed analysis of {len(elements)} elements")
                        # Log first few elements for debugging
                        for i, elem in enumerate(elements[:5]):
                            try:
                                title_text = elem.find_elements(By.CSS_SELECTOR, 'div.fc-event-title')
                                title = title_text[0].text.strip() if title_text else "NO_TITLE"
                                classes = elem.get_attribute('class') or "NO_CLASS"
                                tag = elem.tag_name
                                text_preview = elem.text[:100] if elem.text else "NO_TEXT"
                                logger.info(f"  Element {i}: Tag='{tag}' Class='{classes}' Title='{title}' Text='{text_preview}'")
                            except Exception as debug_e:
                                logger.info(f"  Element {i}: Error getting info: {debug_e}")
                    
                    break
                else:
                    logger.info(f"  ⚠️  No elements found with selector '{selector}'")
            except Exception as e:
                logger.warning(f"  ❌ Selector '{selector}' failed: {e}")
                continue
        
        # If no events found with standard selectors, try alternative approaches
        if not event_elements:
            logger.warning("Standard FullCalendar selectors failed, trying alternative approaches...")
            
            # Try looking for events in table cells
            try:
                table_cells = self.browser.find_elements(By.CSS_SELECTOR, 'td.fc-day')
                logger.info(f"Found {len(table_cells)} table day cells")
                
                for cell in table_cells:
                    # Look for any clickable elements or divs that might be events
                    cell_events = cell.find_elements(By.CSS_SELECTOR, 'a, div[class*="event"], div[class*="fc"]')
                    if cell_events:
                        event_elements.extend(cell_events)
                        logger.info(f"Found {len(cell_events)} potential events in table cell")
                
                if event_elements:
                    used_selector = "table_cell_events"
                    logger.info(f"Total events found via table cells: {len(event_elements)}")
                    
            except Exception as e:
                logger.debug(f"Table cell approach failed: {e}")
            
            # If still no events, try looking for any clickable elements
            if not event_elements:
                try:
                    clickable_elements = self.browser.find_elements(By.CSS_SELECTOR, 'a[href], div[onclick], div[class*="click"]')
                    logger.info(f"Found {len(clickable_elements)} clickable elements")
                    
                    # Filter for elements that might be events
                    for elem in clickable_elements:
                        try:
                            text = elem.text.strip()
                            if text and len(text) > 3 and any(keyword in text.lower() for keyword in ['prayer', 'meeting', 'event', 'service', 'group']):
                                event_elements.append(elem)
                        except:
                            continue
                    
                    if event_elements:
                        used_selector = "clickable_elements"
                        logger.info(f"Total events found via clickable elements: {len(event_elements)}")
                        
                except Exception as e:
                    logger.debug(f"Clickable elements approach failed: {e}")
        
        # Final fallback: Look for any elements with event-like text
        if not event_elements:
            logger.warning("All standard approaches failed, trying text-based event detection...")
            try:
                all_divs = self.browser.find_elements(By.TAG_NAME, 'div')
                event_like_divs = []
                
                for div in all_divs:
                    try:
                        text = div.text.strip()
                        if text and len(text) > 3:
                            # Look for patterns that suggest this is an event
                            if any(keyword in text.lower() for keyword in ['prayer', 'meeting', 'event', 'service', 'group', 'bible', 'worship']):
                                event_like_divs.append(div)
                    except:
                        continue
                
                if event_like_divs:
                    event_elements = event_like_divs
                    used_selector = "text_based_detection"
                    logger.info(f"Found {len(event_elements)} potential events via text analysis")
                    
            except Exception as e:
                logger.debug(f"Text-based detection failed: {e}")
        
        if not event_elements:
            logger.warning("No FullCalendar events found with any selector")
            # Try to understand what's on the page
            try:
                # Look for any elements that might contain event information
                all_divs = self.browser.find_elements(By.TAG_NAME, 'div')
                event_like_divs = [div for div in all_divs if any(keyword in div.get_attribute('class') or keyword in div.get_attribute('id') or keyword in div.text.lower() 
                                                               for keyword in ['event', 'calendar', 'schedule', 'meeting', 'prayer', 'kids', 'bam'])]
                logger.info(f"Found {len(event_like_divs)} divs that might contain event info")
                
                # Save a sample of these elements for debugging
                if event_like_divs and self.save_debug_files:
                    debug_elements = []
                    for i, div in enumerate(event_like_divs[:10]):  # First 10
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
        """Extract event data from any event element by getting text directly"""
        try:
            # Get the text content directly from the element
            title = event_element.text.strip()
            if not title or len(title) < 3:
                return None
            
            # For now, use the current month/year context since we can't determine exact dates
            # This is a limitation but will at least get us events
            try:
                # Parse month name to number
                month_num = datetime.strptime(month, '%B').month
                year_num = int(year)
                # Use the first day of the month as a fallback
                date_str = f"{year_num}-{month_num:02d}-01"
            except:
                # Use current date as fallback
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            # Parse the date
            try:
                event_date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                logger.warning(f"Could not parse date: {date_str}")
                return None
            
            # Create a simple event object
            event = {
                'title': title,
                'start': event_date.replace(hour=0, minute=0, second=0, microsecond=0),
                'end': event_date.replace(hour=23, minute=59, second=0, microsecond=0),
                'date': date_str,
                'time': "All day",  # Default to all-day since we can't determine time
                'month': month,
                'year': year,
                'calendar_type': calendar_type,
                'url': f"https://antiochboone.com/calendar-{calendar_type}",
                'all_day': True,
                'source': 'Subsplash',
                'location': 'Antioch Boone',
                'unique_id': f"{calendar_type}_{date_str}_{title.lower().replace(' ', '_')}"
            }
            
            logger.info(f"✅ Extracted event: '{title}' from element with class '{event_element.get_attribute('class')}'")
            return event
            
        except Exception as e:
            logger.warning(f"Error extracting event from element: {str(e)}")
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
                        # Sync to Google Calendar
                        sync_result = self.sync_events_to_google_calendar(events, calendar_type)
                        sync_results['calendar_results'][calendar_type] = sync_result
                        sync_results['total_events_processed'] += len(events)
                        
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