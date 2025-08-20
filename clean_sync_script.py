#!/usr/bin/env python3
"""
Clean Subsplash to Google Calendar Sync Script
This script provides a focused, effective approach to syncing events from Subsplash to Google Calendar.
"""

import os
import json
import re
import time
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Optional, Tuple

# Google Calendar imports
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SubsplashCalendarSync:
    """Clean implementation of Subsplash to Google Calendar sync"""
    
    def __init__(self, calendar_config: Dict):
        self.calendar_config = calendar_config
        self.calendar_service = None
        self.driver = None
        
        # Configuration
        self.max_months_to_check = int(os.environ.get('MAX_MONTHS_TO_CHECK', '6'))
        self.max_consecutive_empty_months = int(os.environ.get('MAX_CONSECUTIVE_EMPTY_MONTHS', '3'))
        self.browser_wait_time = int(os.environ.get('BROWSER_WAIT_TIME', '10'))
        
        logger.info(f"Initialized sync for calendar: {calendar_config['name']}")
        logger.info(f"Target URL: {calendar_config['subsplash_url']}")
        logger.info(f"Google Calendar ID: {calendar_config['google_calendar_id']}")
    
    def authenticate_google(self) -> bool:
        """Authenticate with Google Calendar API"""
        try:
            # Check for OAuth credentials file
            credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'oauth_credentials.json')
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
                    # For GitHub Actions, we need to handle headless authentication
                    if os.getenv('GITHUB_ACTIONS') == 'true':
                        logger.error("OAuth 2.0 interactive flow not supported in GitHub Actions")
                        logger.info("Please run this locally first to generate a token.pickle file")
                        return False
                    else:
                        # Local development - interactive flow
                        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, ['https://www.googleapis.com/auth/calendar'])
                        creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                try:
                    with open(token_file, 'wb') as token:
                        pickle.dump(creds, token)
                    logger.info("Saved OAuth token for future use")
                except Exception as e:
                    logger.warning(f"Could not save token: {str(e)}")
            
            # Build service
            self.calendar_service = build('calendar', 'v3', credentials=creds)
            logger.info("Google Calendar authentication successful")
            return True
                
        except Exception as e:
            logger.error(f"Google Calendar authentication failed: {str(e)}")
            return False
    
    def setup_browser(self) -> bool:
        """Setup Chrome browser for web scraping"""
        try:
            chrome_options = Options()
            
            # Headless mode for production
            if os.getenv('GITHUB_ACTIONS') == 'true':
                chrome_options.add_argument('--headless')
            
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
    
    def scrape_events_with_browser_navigation(self) -> List[Dict]:
        """Scrape events by navigating through calendar months using browser automation"""
        events = []
        
        try:
            if not self.setup_browser():
                return events
            
            # Navigate to the calendar page
            logger.info(f"Navigating to: {self.calendar_config['subsplash_url']}")
            self.driver.get(self.calendar_config['subsplash_url'])
            
            # Wait for page to load
            time.sleep(self.browser_wait_time)
            
            consecutive_empty_months = 0
            months_checked = 0
            
            while (months_checked < self.max_months_to_check and 
                   consecutive_empty_months < self.max_consecutive_empty_months):
                
                # Extract events from current month
                current_month_events = self._extract_events_from_current_page()
                
                if current_month_events:
                    events.extend(current_month_events)
                    consecutive_empty_months = 0
                    logger.info(f"Month {months_checked + 1}: Found {len(current_month_events)} events")
                else:
                    consecutive_empty_months += 1
                    logger.info(f"Month {months_checked + 1}: No events found (consecutive empty: {consecutive_empty_months})")
                
                months_checked += 1
                
                # Try to navigate to next month
                if not self._navigate_to_next_month():
                    logger.info("Could not navigate to next month, stopping")
                    break
                
                # Wait for page to load
                time.sleep(self.browser_wait_time)
            
            logger.info(f"Browser navigation complete. Found {len(events)} total events across {months_checked} months.")
            return events
            
        except Exception as e:
            logger.error(f"Error during browser navigation scraping: {str(e)}")
            return events
        finally:
            if self.driver:
                self.driver.quit()
    
    def _extract_events_from_current_page(self) -> List[Dict]:
        """Extract events from the current calendar page"""
        events = []
        
        try:
            # Wait for calendar content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Try multiple selectors to find events
            event_selectors = [
                'div.kit-list-item__text',
                'div.kit-list-item',
                'div[class*="list-item"]',
                'div[class*="event"]',
                'div[class*="calendar"]',
                'article',
                'li',
                'div[data-testid*="event"]',
                'div[class*="subsplash"]',
                'div[class*="kit"]',
                'div[class*="item"]',
                'div[class*="entry"]',
                'div[class*="post"]'
            ]
            
            for selector in event_selectors:
                try:
                    event_elements = soup.select(selector)
                    if event_elements:
                        logger.info(f"Found {len(event_elements)} elements with selector: {selector}")
                        
                        for element in event_elements:
                            event = self._extract_event_from_element(element)
                            if event:
                                events.append(event)
                        
                        if events:
                            break  # Found events, no need to try other selectors
                            
                except Exception as e:
                    logger.warning(f"Error with selector {selector}: {str(e)}")
                    continue
            
            # If no events found with selectors, try text analysis
            if not events:
                logger.info("No events found with selectors, trying text analysis...")
                text_events = self._extract_events_from_text(soup)
                if text_events:
                    events.extend(text_events)
                    logger.info(f"Text analysis found {len(text_events)} events")
            
            return events
            
        except Exception as e:
            logger.error(f"Error extracting events from current page: {str(e)}")
            return events
    
    def _extract_event_from_element(self, element) -> Optional[Dict]:
        """Extract event data from a single HTML element"""
        try:
            # Get text content
            text_content = element.get_text(strip=True)
            if not text_content or len(text_content) < 5:
                return None
            
            # Try to extract title (first line that looks like an event title)
            lines = text_content.split('\n')
            title = None
            
            for line in lines:
                line = line.strip()
                if (line and len(line) > 3 and len(line) < 100 and 
                    not self._looks_like_datetime(line) and 
                    line[0].isupper()):
                    title = line
                    break
            
            if not title:
                return None
            
            # Try to extract datetime information
            datetime_info = self._extract_datetime_from_text(text_content)
            if not datetime_info:
                return None
            
            start_time, end_time = datetime_info
            
            # Create event object
            event = {
                'title': title,
                'start': start_time,
                'end': end_time,
                'description': text_content,
                'location': self.calendar_config.get('location', 'Antioch Boone'),
                'all_day': self._is_all_day_event(start_time, end_time)
            }
            
            return event
            
        except Exception as e:
            logger.warning(f"Error extracting event from element: {str(e)}")
            return None
    
    def _extract_datetime_from_text(self, text: str) -> Optional[Tuple[datetime, datetime]]:
        """Extract datetime information from text"""
        try:
            # Common date patterns
            date_patterns = [
                r'([A-Za-z]+ \d{1,2},? \d{4})',
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{1,2}-\d{1,2}-\d{4})'
            ]
            
            # Time patterns
            time_patterns = [
                r'(\d{1,2}:\d{2}[ap]m)',
                r'(\d{1,2}:\d{2} [ap]m)',
                r'(\d{1,2}:\d{2})'
            ]
            
            # Find dates
            dates = []
            for pattern in date_patterns:
                matches = re.findall(pattern, text)
                dates.extend(matches)
            
            # Find times
            times = []
            for pattern in time_patterns:
                matches = re.findall(pattern, text)
                times.extend(matches)
            
            if not dates:
                return None
            
            # Parse the first date found
            date_str = dates[0]
            try:
                # Try different date formats
                for fmt in ['%B %d, %Y', '%B %d %Y', '%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y']:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    # If no format worked, try dateutil
                    from dateutil import parser
                    parsed_date = parser.parse(date_str)
            except:
                return None
            
            # Parse time if available
            start_time = parsed_date
            end_time = parsed_date + timedelta(hours=1)  # Default 1 hour duration
            
            if times:
                try:
                    time_str = times[0]
                    # Parse time
                    if 'pm' in time_str.lower():
                        time_str = time_str.replace('pm', '').replace('PM', '').strip()
                        hour = int(time_str.split(':')[0])
                        if hour != 12:
                            hour += 12
                        minute = int(time_str.split(':')[1])
                    elif 'am' in time_str.lower():
                        time_str = time_str.replace('am', '').replace('AM', '').strip()
                        hour = int(time_str.split(':')[0])
                        if hour == 12:
                            hour = 0
                        minute = int(time_str.split(':')[1])
                    else:
                        hour, minute = map(int, time_str.split(':'))
                    
                    start_time = parsed_date.replace(hour=hour, minute=minute)
                    end_time = start_time + timedelta(hours=1)
                except:
                    pass
            
            return start_time, end_time
            
        except Exception as e:
            logger.warning(f"Error extracting datetime from text: {str(e)}")
            return None
    
    def _looks_like_datetime(self, text: str) -> bool:
        """Check if text looks like a datetime string"""
        datetime_indicators = [
            'am', 'pm', 'edt', 'est', 'from', 'to', 'august', 'september', 'october', 
            'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june', 'july'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in datetime_indicators)
    
    def _is_all_day_event(self, start_time: datetime, end_time: datetime) -> bool:
        """Check if event is all-day based on start and end times"""
        if not start_time or not end_time:
            return False
        
        # Check if times are midnight (all-day events typically start/end at midnight)
        return (start_time.hour == 0 and start_time.minute == 0 and 
                end_time.hour == 0 and end_time.minute == 0)
    
    def _extract_events_from_text(self, soup) -> List[Dict]:
        """Fallback method to extract events from page text"""
        events = []
        
        try:
            # Get all text from the page
            all_text = soup.get_text()
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            
            # Look for lines that might be event titles
            for line in lines:
                if (len(line) > 10 and len(line) < 100 and 
                    line[0].isupper() and 
                    not self._looks_like_datetime(line)):
                    
                    # Try to create a basic event
                    event = self._create_event_from_text_line(line)
                    if event:
                        events.append(event)
            
            return events
            
        except Exception as e:
            logger.warning(f"Error extracting events from text: {str(e)}")
            return events
    
    def _create_event_from_text_line(self, text_line: str) -> Optional[Dict]:
        """Create a basic event from a text line"""
        try:
            # This is a fallback method - we'll create a basic event
            # with today's date and the text as title
            today = datetime.now()
            
            event = {
                'title': text_line,
                'start': today,
                'end': today + timedelta(hours=1),
                'description': text_line,
                'location': self.calendar_config.get('location', 'Antioch Boone'),
                'all_day': False
            }
            
            return event
            
        except Exception as e:
            logger.warning(f"Error creating event from text line: {str(e)}")
            return None
    
    def _navigate_to_next_month(self) -> bool:
        """Navigate to the next month using calendar navigation arrows"""
        try:
            # Look for next month navigation elements
            next_selectors = [
                'button[aria-label*="next"]',
                'button[aria-label*="Next"]',
                'button[title*="next"]',
                'button[title*="Next"]',
                'a[aria-label*="next"]',
                'a[aria-label*="Next"]',
                'a[title*="next"]',
                'a[title*="Next"]',
                'button[class*="next"]',
                'a[class*="next"]',
                'button[class*="arrow"]',
                'a[class*="arrow"]',
                'button[class*="nav"]',
                'a[class*="nav"]',
                # More specific Subsplash selectors
                'button[data-testid*="next"]',
                'button[data-testid*="arrow"]',
                'a[data-testid*="next"]',
                'a[data-testid*="arrow"]',
                # Look for any button/link with next-related text
                'button:contains("Next")',
                'a:contains("Next")',
                'button:contains(">")',
                'a:contains(">")',
                'button:contains("→")',
                'a:contains("→")'
            ]
            
            for selector in next_selectors:
                try:
                    # Try to find the element
                    if ':contains' in selector:
                        # Handle :contains pseudo-selector manually
                        text_to_find = selector.split('"')[1]
                        elements = self.driver.find_elements(By.TAG_NAME, selector.split(':')[0])
                        for element in elements:
                            if text_to_find in element.text:
                                element.click()
                                logger.info(f"Clicked next navigation element with text: {text_to_find}")
                                return True
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            elements[0].click()
                            logger.info(f"Clicked next navigation element with selector: {selector}")
                            return True
                            
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {str(e)}")
                    continue
            
            # If no specific selectors worked, try to find any clickable element that might be next
            try:
                # Look for any button or link that might be navigation
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                
                # Check buttons for next-like text
                for button in all_buttons:
                    button_text = button.text.lower()
                    if any(word in button_text for word in ['next', '>', '→', 'arrow', 'forward']):
                        button.click()
                        logger.info("Clicked button with next-like text")
                        return True
                
                # Check links for next-like text
                for link in all_links:
                    link_text = link.text.lower()
                    if any(word in link_text for word in ['next', '>', '→', 'arrow', 'forward']):
                        link.click()
                        logger.info("Clicked link with next-like text")
                        return True
                        
            except Exception as e:
                logger.debug(f"Fallback navigation failed: {str(e)}")
            
            logger.warning("Could not find next month navigation element")
            return False
            
        except Exception as e:
            logger.error(f"Error navigating to next month: {str(e)}")
            return False
    
    def sync_to_google_calendar(self, events: List[Dict]) -> bool:
        """Sync events to Google Calendar"""
        try:
            if not self.calendar_service:
                logger.error("Google Calendar service not initialized")
                return False
            
            logger.info(f"Starting sync of {len(events)} events to Google Calendar")
            
            # Get existing events for comparison
            existing_events = self._get_existing_events()
            existing_event_map = self._create_event_map(existing_events)
            
            synced_count = 0
            updated_count = 0
            skipped_count = 0
            
            for event_data in events:
                # Create event key for comparison
                event_key = self._create_event_key(event_data)
                
                # Check if event already exists
                if event_key and event_key in existing_event_map:
                    # Update existing event
                    existing_event = existing_event_map[event_key]
                    try:
                        google_event = self._prepare_google_event(event_data)
                        self.calendar_service.events().update(
                            calendarId=self.calendar_config['google_calendar_id'],
                            eventId=existing_event['id'],
                            body=google_event
                        ).execute()
                        updated_count += 1
                        logger.info(f"Updated event: {event_data['title']}")
                    except Exception as e:
                        logger.error(f"Error updating event {event_data['title']}: {str(e)}")
                else:
                    # Create new event
                    try:
                        google_event = self._prepare_google_event(event_data)
                        self.calendar_service.events().insert(
                            calendarId=self.calendar_config['google_calendar_id'],
                            body=google_event
                        ).execute()
                        synced_count += 1
                        logger.info(f"Created event: {event_data['title']}")
                    except Exception as e:
                        logger.error(f"Error creating event {event_data['title']}: {str(e)}")
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
            
            logger.info(f"Sync complete: {synced_count} new events, {updated_count} updated events, {skipped_count} skipped")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing to Google Calendar: {str(e)}")
            return False
    
    def _get_existing_events(self) -> List[Dict]:
        """Get existing events from Google Calendar"""
        try:
            # Get events from the last 6 months to 2 years in the future
            now = datetime.utcnow()
            start_time = (now - timedelta(days=180)).isoformat() + 'Z'
            end_time = (now + timedelta(days=730)).isoformat() + 'Z'
            
            events_result = self.calendar_service.events().list(
                calendarId=self.calendar_config['google_calendar_id'],
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
            
        except Exception as e:
            logger.error(f"Error getting existing events: {str(e)}")
            return []
    
    def _create_event_map(self, events: List[Dict]) -> Dict[str, Dict]:
        """Create a map of events for quick lookup"""
        event_map = {}
        
        for event in events:
            try:
                title = event.get('summary', '').strip()
                start_time = event.get('start', {}).get('dateTime') or event.get('start', {}).get('date')
                
                if title and start_time:
                    # Parse the start time
                    if 'T' in start_time:
                        # Has time component
                        parsed_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        key = f"{title.lower()}_{parsed_time.strftime('%Y-%m-%d_%H:%M')}"
                    else:
                        # All-day event
                        parsed_date = datetime.fromisoformat(start_time)
                        key = f"{title.lower()}_{parsed_date.strftime('%Y-%m-%d')}_allday"
                    
                    event_map[key] = event
                    
            except Exception as e:
                logger.warning(f"Could not create key for event: {str(e)}")
                continue
        
        return event_map
    
    def _create_event_key(self, event_data: Dict) -> Optional[str]:
        """Create a unique key for an event"""
        try:
            title = event_data.get('title', '').strip()
            start = event_data.get('start')
            
            if not title or not start:
                return None
            
            if isinstance(start, datetime):
                if event_data.get('all_day', False):
                    key = f"{title.lower()}_{start.strftime('%Y-%m-%d')}_allday"
                else:
                    key = f"{title.lower()}_{start.strftime('%Y-%m-%d_%H:%M')}"
            else:
                key = f"{title.lower()}_{str(start)}"
            
            return key
            
        except Exception as e:
            logger.warning(f"Could not create event key: {str(e)}")
            return None
    
    def _prepare_google_event(self, event_data: Dict) -> Dict:
        """Prepare event data for Google Calendar API"""
        google_event = {
            'summary': event_data['title'],
            'description': event_data.get('description', ''),
            'location': event_data.get('location', ''),
        }
        
        if event_data.get('all_day', False):
            google_event['start'] = {'date': event_data['start'].date().isoformat()}
            google_event['end'] = {'date': event_data['end'].date().isoformat()}
        else:
            google_event['start'] = {
                'dateTime': event_data['start'].isoformat(),
                'timeZone': 'America/New_York'
            }
            google_event['end'] = {
                'dateTime': event_data['end'].isoformat(),
                'timeZone': 'America/New_York'
            }
        
        return google_event
    
    def run_sync(self) -> bool:
        """Main sync method"""
        try:
            logger.info(f"Starting sync for {self.calendar_config['name']}")
            
            # Step 1: Authenticate with Google Calendar
            if not self.authenticate_google():
                logger.error("Google Calendar authentication failed")
                return False
            
            # Step 2: Scrape events from Subsplash using browser navigation
            logger.info("Scraping events from Subsplash using browser navigation...")
            events = self.scrape_events_with_browser_navigation()
            
            if not events:
                logger.warning("No events found to sync")
                return True  # Not a failure, just no events
            
            logger.info(f"Found {len(events)} events to sync")
            
            # Step 3: Sync events to Google Calendar
            if self.sync_to_google_calendar(events):
                logger.info("Sync completed successfully")
                return True
            else:
                logger.error("Sync to Google Calendar failed")
                return False
            
        except Exception as e:
            logger.error(f"Error during sync: {str(e)}")
            return False

def main():
    """Main function for GitHub Actions"""
    logger.info("Starting Subsplash calendar sync process...")
    
    # Calendar configuration
    calendar_configs = {
        'bam': {
            'name': 'BAM',
            'subsplash_url': 'https://antiochboone.com/calendar-bam',
            'google_calendar_id': os.environ.get('BAM_CALENDAR_ID'),
            'location': 'Antioch Boone'
        },
        'kids': {
            'name': 'Kingdom Kids',
            'subsplash_url': 'https://antiochboone.com/calendar-kids',
            'google_calendar_id': os.environ.get('KIDS_CALENDAR_ID'),
            'location': 'Antioch Boone'
        },
        'prayer': {
            'name': 'Prayer',
            'subsplash_url': 'https://antiochboone.com/calendar-prayer',
            'google_calendar_id': os.environ.get('PRAYER_CALENDAR_ID'),
            'location': 'Antioch Boone'
        }
    }
    
    # Get enabled calendars
    enabled_calendars = {k: v for k, v in calendar_configs.items() 
                        if v['google_calendar_id']}
    
    if not enabled_calendars:
        logger.error("No enabled calendars found with valid Google Calendar IDs")
        exit(1)
    
    logger.info(f"Found {len(enabled_calendars)} enabled calendars")
    
    # Sync each enabled calendar
    overall_success = True
    for calendar_key, calendar_config in enabled_calendars.items():
        logger.info(f"Syncing calendar: {calendar_config['name']}")
        
        try:
            sync_service = SubsplashCalendarSync(calendar_config)
            success = sync_service.run_sync()
            
            if success:
                logger.info(f"{calendar_config['name']} sync completed successfully!")
            else:
                logger.error(f"{calendar_config['name']} sync failed!")
                overall_success = False
                
        except Exception as e:
            logger.error(f"Error syncing {calendar_config['name']}: {str(e)}")
            overall_success = False
    
    if overall_success:
        logger.info("All calendar syncs completed successfully!")
        exit(0)
    else:
        logger.error("Some calendar syncs failed!")
        exit(1)

if __name__ == "__main__":
    main()
