#!/usr/bin/env python3
"""
Test Script: Single Month Prayer Calendar Sync
This script tests the duplicate prevention fixes by syncing only the Prayer calendar for August
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestPrayerCalendarSync:
    """Test class for syncing only the Prayer calendar for August"""
    
    def __init__(self):
        self.driver = None
        self.google_service = None
        
        # Only test with prayer calendar
        self.calendar_id = os.getenv('PRAYER_CALENDAR_ID')
        self.calendar_url = 'https://antiochboone.com/calendar-prayer'
        
        # Expected events for August 2025
        self.expected_events = [
            {
                'title': 'Early Morning Prayer',
                'date': '2025-08-21',
                'time': '6:30a',
                'expected_start': '2025-08-21 06:30:00',
                'expected_end': '2025-08-21 07:30:00'
            },
            {
                'title': 'Prayer Set',
                'date': '2025-08-26', 
                'time': '5:15p',
                'expected_start': '2025-08-26 17:15:00',
                'expected_end': '2025-08-26 18:15:00'
            },
            {
                'title': 'Early Morning Prayer',
                'date': '2025-08-28',
                'time': '6:30a', 
                'expected_start': '2025-08-28 06:30:00',
                'expected_end': '2025-08-28 07:30:00'
            }
        ]
        
        logger.info("🧪 Test Prayer Calendar Sync Initialized")
        logger.info(f"Calendar ID: {self.calendar_id}")
        logger.info(f"Expected Events: {len(self.expected_events)}")
    
    def setup_browser(self) -> bool:
        """Setup Chrome browser for web scraping"""
        try:
            chrome_options = Options()
            
            # Test mode - visible browser for debugging
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
    
    def setup_google_calendar(self) -> bool:
        """Setup Google Calendar API service using OAuth 2.0"""
        try:
            # Check if we have OAuth credentials
            credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
            if not os.path.exists(credentials_file):
                logger.error(f"Google credentials file not found: {credentials_file}")
                return False
            
            # Load OAuth 2.0 credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            import pickle
            
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
    
    def scrape_august_events(self) -> List[Dict]:
        """Scrape only August events from the Prayer calendar"""
        events = []
        
        try:
            if not self.setup_browser():
                return events
            
            logger.info(f"🔍 Navigating to Prayer calendar: {self.calendar_url}")
            self.driver.get(self.calendar_url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Verify we're on August
            month_year_element = self.driver.find_element(By.CLASS_NAME, "fc-toolbar-title")
            month_year_text = month_year_element.text.strip()
            logger.info(f"📅 Calendar shows: {month_year_text}")
            
            if "August 2025" not in month_year_text:
                logger.warning(f"⚠️ Expected August 2025, but calendar shows: {month_year_text}")
                # Try to navigate to August if needed
                # (This is a simplified version - in production you'd navigate properly)
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Look specifically for FullCalendar events
            fc_events = soup.find_all('a', class_='fc-event')
            logger.info(f"🔍 Found {len(fc_events)} FullCalendar event elements")
            
            for i, event_element in enumerate(fc_events):
                try:
                    event = self._extract_fc_event(event_element, 'August', '2025', 'prayer')
                    if event:
                        events.append(event)
                        logger.info(f"✅ Event {i+1}: {event['title']} on {event['start']}")
                except Exception as e:
                    logger.warning(f"⚠️ Error extracting event {i+1}: {str(e)}")
                    continue
            
            return events
            
        except Exception as e:
            logger.error(f"❌ Error scraping August events: {str(e)}")
            return events
        finally:
            if self.driver:
                self.driver.quit()
    
    def _extract_fc_event(self, event_element, month: str, year: str, calendar_type: str) -> Optional[Dict]:
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
            
            date_str = date_cell.get('data-date')
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
            
            # Convert relative URLs to absolute URLs for Google Calendar
            if event_url and event_url.startswith('/'):
                event_url = f"https://antiochboone.com{event_url}"
            elif not event_url:
                event_url = "https://antiochboone.com/calendar-prayer"
            
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
                'location': 'Antioch Boone',
                'unique_id': f"{calendar_type}_{date_str}_{title.lower().replace(' ', '_')}"
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
        
        return (start_time.hour == 0 and start_time.minute == 0 and 
                end_time.hour == 0 and end_time.minute == 0)
    
    def sync_events_to_google_calendar(self, events: List[Dict]) -> Dict:
        """Sync events to Google Calendar"""
        if not self.google_service:
            logger.error("Google Calendar service not initialized")
            return {'success': False, 'error': 'Google Calendar service not initialized'}
        
        if not self.calendar_id:
            logger.error("No Prayer Calendar ID found")
            return {'success': False, 'error': 'No Prayer Calendar ID configured'}
        
        results = {
            'success': True,
            'calendar_type': 'prayer',
            'total_events': len(events),
            'created': 0,
            'updated': 0,
            'errors': 0,
            'error_details': []
        }
        
        for event in events:
            try:
                # Check if event already exists
                existing_event = self._find_existing_event(event)
                
                if existing_event:
                    # Update existing event
                    updated_event = self._update_google_calendar_event(existing_event['id'], event)
                    if updated_event:
                        results['updated'] += 1
                        logger.info(f"✅ Updated event: {event['title']}")
                    else:
                        results['errors'] += 1
                        results['error_details'].append(f"Failed to update: {event['title']}")
                else:
                    # Create new event
                    created_event = self._create_google_calendar_event(event)
                    if created_event:
                        results['created'] += 1
                        logger.info(f"✅ Created event: {event['title']}")
                    else:
                        results['errors'] += 1
                        results['error_details'].append(f"Failed to create: {event['title']}")
                
            except Exception as e:
                results['errors'] += 1
                error_msg = f"Error processing {event['title']}: {str(e)}"
                results['error_details'].append(error_msg)
                logger.error(error_msg)
        
        return results
    
    def _find_existing_event(self, event: Dict) -> Optional[Dict]:
        """Find existing event in Google Calendar"""
        try:
            # Search for events with similar title and time
            time_min = event['start'].isoformat() + 'Z'
            time_max = (event['start'] + timedelta(days=1)).isoformat() + 'Z'
            
            events_result = self.google_service.events().list(
                calendarId=self.calendar_id,
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
                                logger.info(f"🔍 Found existing event: {event['title']} on {existing_date}")
                                return existing_event
                        except (IndexError, ValueError):
                            continue
            
            logger.info(f"🔍 No existing event found for: {event['title']} on {event['date']}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding existing event: {str(e)}")
            return None
    
    def _create_google_calendar_event(self, event: Dict) -> Optional[Dict]:
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
                calendarId=self.calendar_id,
                body=google_event
            ).execute()
            
            return created_event
            
        except Exception as e:
            logger.error(f"Error creating Google Calendar event: {str(e)}")
            return None
    
    def _update_google_calendar_event(self, event_id: str, event: Dict) -> Optional[Dict]:
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
                calendarId=self.calendar_id,
                eventId=event_id,
                body=google_event
            ).execute()
            
            return updated_event
            
        except Exception as e:
            logger.error(f"Error updating Google Calendar event: {str(e)}")
            return None
    
    def run_test_sync(self) -> Dict:
        """Run the test sync for Prayer calendar August events"""
        logger.info("🧪 Starting Test Prayer Calendar Sync")
        
        # Setup Google Calendar
        if not self.setup_google_calendar():
            return {'success': False, 'error': 'Failed to setup Google Calendar'}
        
        # Scrape August events
        events = self.scrape_august_events()
        logger.info(f"📊 Scraped {len(events)} events from August")
        
        if not events:
            return {'success': False, 'error': 'No events found in August'}
        
        # Verify we found the expected events
        self._verify_expected_events(events)
        
        # Sync to Google Calendar
        sync_result = self.sync_events_to_google_calendar(events)
        
        return {
            'success': True,
            'scraped_events': len(events),
            'sync_result': sync_result,
            'events': events
        }
    
    def _verify_expected_events(self, events: List[Dict]):
        """Verify that we found the expected events"""
        logger.info("🔍 Verifying Expected Events")
        
        found_titles = [event['title'] for event in events]
        found_dates = [event['date'] for event in events]
        
        for expected in self.expected_events:
            if expected['title'] in found_titles and expected['date'] in found_dates:
                logger.info(f"✅ Found expected event: {expected['title']} on {expected['date']}")
            else:
                logger.warning(f"⚠️ Missing expected event: {expected['title']} on {expected['date']}")

def main():
    """Main test function"""
    print("🧪 TEST: Single Month Prayer Calendar Sync")
    print("=" * 60)
    print("This test will:")
    print("1. Scrape only August events from Prayer calendar")
    print("2. Verify we found the expected 3 events")
    print("3. Sync to Google Calendar (create/update)")
    print("4. Test the duplicate prevention fixes")
    print("=" * 60)
    print()
    
    # Create test sync instance
    test_sync = TestPrayerCalendarSync()
    
    # Run test sync
    results = test_sync.run_test_sync()
    
    # Display results
    print("\n" + "="*60)
    print("🧪 TEST RESULTS")
    print("="*60)
    
    if results['success']:
        print(f"✅ Test completed successfully!")
        print(f"📊 Events scraped: {results['scraped_events']}")
        
        sync_result = results['sync_result']
        print(f"📅 Sync results:")
        print(f"   Created: {sync_result['created']}")
        print(f"   Updated: {sync_result['updated']}")
        print(f"   Errors: {sync_result['errors']}")
        
        if sync_result['errors'] > 0:
            print(f"   Error details:")
            for error in sync_result['error_details']:
                print(f"     - {error}")
        
        print()
        print("🎯 Next Steps:")
        print("1. Check your Google Calendar for the Prayer events")
        print("2. Verify no duplicate events were created")
        print("3. If successful, the full sync should work correctly")
        
    else:
        print(f"❌ Test failed: {results.get('error', 'Unknown error')}")
    
    print("="*60)
    
    # Save results to file
    with open('test_prayer_sync_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("Test results saved to test_prayer_sync_results.json")

if __name__ == "__main__":
    main()
