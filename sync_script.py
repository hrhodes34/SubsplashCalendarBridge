#!/usr/bin/env python3
"""
Subsplash to Google Calendar Sync Script
This script runs automatically via GitHub Actions to sync events from Subsplash to Google Calendar.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time

# Configuration
SCOPES = ['https://www.googleapis.com/auth/calendar']
GOOGLE_CALENDAR_ID = os.environ.get('GOOGLE_CALENDAR_ID')
SUBSPLASH_EMBED_URL = os.environ.get('SUBSPLASH_EMBED_URL')

class SubsplashSyncService:
    def __init__(self):
        self.calendar_service = None
        self.credentials = None
        
    def authenticate_google(self):
        """Authenticate with Google Calendar API using Service Account"""
        try:
            # Load service account credentials from file created by GitHub Actions
            if os.path.exists('credentials.json'):
                # For Service Accounts, we use service_account.Credentials
                self.credentials = service_account.Credentials.from_service_account_file(
                    'credentials.json',
                    scopes=SCOPES
                )
                
                # Build service
                self.calendar_service = build('calendar', 'v3', credentials=self.credentials)
                print("✅ Google Calendar authentication successful")
                return True
            else:
                print("❌ credentials.json not found")
                return False
                
        except Exception as e:
            print(f"❌ Google Calendar authentication failed: {str(e)}")
            return False
    
    def scrape_subsplash_events(self):
        """
        Scrape real events from Subsplash calendar
        """
        try:
            print("�� Scraping Subsplash events...")
            
            # Subsplash embed URL from your calendar
            subsplash_url = "https://subsplash.com/+wrmm/lb/ca/+pysr4r6?embed"
            
            # Fetch the page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(subsplash_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all event items
            event_items = soup.find_all('div', class_='kit-list-item__text')
            
            events = []
            for item in event_items:
                try:
                    # Extract title
                    title_elem = item.find('h2', class_='kit-list-item__title')
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Extract date and time
                    subtitle_elem = item.find('h3', class_='kit-list-item__subtitle')
                    if not subtitle_elem:
                        continue
                    
                    date_time_text = subtitle_elem.get_text(strip=True)
                    # Parse date and time (format: "August 20, 2025 from 6:00 - 8:00pm EDT")
                    parsed_datetime = self._parse_subsplash_datetime(date_time_text)
                    if not parsed_datetime:
                        continue
                    
                    start_time, end_time = parsed_datetime
                    
                    # Extract description
                    summary_elem = item.find('p', class_='kit-list-item__summary')
                    description = summary_elem.get_text(strip=True) if summary_elem else ""
                    
                    # Create event
                    event = {
                        'title': title,
                        'start': start_time,
                        'end': end_time,
                        'description': description,
                        'location': 'Antioch Boone',  # Default location
                        'all_day': False
                    }
                    
                    events.append(event)
                    print(f"📅 Found event: {title} on {start_time.strftime('%B %d, %Y')}")
                    
                except Exception as e:
                    print(f"⚠️ Error parsing event: {str(e)}")
                    continue
            
            print(f"✅ Found {len(events)} events from Subsplash")
            return events
            
        except Exception as e:
            print(f"❌ Error scraping Subsplash events: {str(e)}")
            return []
    
    def _parse_subsplash_datetime(self, date_time_text):
        """
        Parse Subsplash date/time formats:
        - "August 20, 2025 from 6:00 - 8:00pm EDT" (single day)
        - "August 22, 6:00pm - August 24, 2025 11:00am EDT" (multi-day)
        Returns (start_datetime, end_datetime) or None if parsing fails
        """
        try:
            import re
            from dateutil import parser
            
            # Try single-day format first: "August 20, 2025 from 6:00 - 8:00pm EDT"
            single_day_pattern = r'([A-Za-z]+ \d{1,2}, \d{4}) from (\d{1,2}:\d{2})([ap]m) - (\d{1,2}:\d{2})([ap]m)'
            single_match = re.search(single_day_pattern, date_time_text)
            
            if single_match:
                date_str = single_match.group(1)  # "August 20, 2025"
                start_time_str = single_match.group(2)  # "6:00"
                start_ampm = single_match.group(3)  # "pm"
                end_time_str = single_match.group(4)   # "8:00"
                end_ampm = single_match.group(5)       # "pm"
                
                # Parse the date
                date_obj = parser.parse(date_str)
                
                # Parse start time
                start_hour, start_minute = map(int, start_time_str.split(':'))
                if start_ampm.lower() == 'pm' and start_hour != 12:
                    start_hour += 12
                elif start_ampm.lower() == 'am' and start_hour == 12:
                    start_hour = 0
                
                start_datetime = date_obj.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
                
                # Parse end time
                end_hour, end_minute = map(int, end_time_str.split(':'))
                if end_ampm.lower() == 'pm' and end_hour != 12:
                    end_hour += 12
                elif end_ampm.lower() == 'am' and end_hour == 12:
                    end_hour = 0
                
                end_datetime = date_obj.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
                
                return start_datetime, end_datetime
            
            # Try multi-day format: "August 22, 6:00pm - August 24, 2025 11:00am EDT"
            multi_day_pattern = r'([A-Za-z]+ \d{1,2}), (\d{1,2}:\d{2})([ap]m) - ([A-Za-z]+ \d{1,2}, \d{4}) (\d{1,2}:\d{2})([ap]m)'
            multi_match = re.search(multi_day_pattern, date_time_text)
            
            if multi_match:
                start_date_str = multi_match.group(1)  # "August 22"
                start_time_str = multi_match.group(2)  # "6:00"
                start_ampm = multi_match.group(3)      # "pm"
                end_date_str = multi_match.group(4)    # "August 24, 2025"
                end_time_str = multi_match.group(5)    # "11:00"
                end_ampm = multi_match.group(6)        # "am"
                
                # Parse start date and time
                start_date_obj = parser.parse(start_date_str + ", 2025")  # Assume current year
                start_hour, start_minute = map(int, start_time_str.split(':'))
                if start_ampm.lower() == 'pm' and start_hour != 12:
                    start_hour += 12
                elif start_ampm.lower() == 'am' and start_hour == 12:
                    start_hour = 0
                
                start_datetime = start_date_obj.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
                
                # Parse end date and time
                end_date_obj = parser.parse(end_date_str)
                end_hour, end_minute = map(int, end_time_str.split(':'))
                if end_ampm.lower() == 'pm' and end_hour != 12:
                    end_hour += 12
                elif end_ampm.lower() == 'am' and end_hour == 12:
                    end_hour = 0
                
                end_datetime = end_date_obj.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
                
                return start_datetime, end_datetime
            
            print(f"⚠️ Could not parse date/time: {date_time_text}")
            return None
            
        except Exception as e:
            print(f"⚠️ Error parsing datetime '{date_time_text}': {str(e)}")
            return None

    def get_existing_google_events(self, start_date, end_date):
        """Get existing events from Google Calendar"""
        try:
            events_result = self.calendar_service.events().list(
                calendarId=GOOGLE_CALENDAR_ID,
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            print(f"📅 Found {len(events)} existing events in Google Calendar")
            return events
            
        except Exception as e:
            print(f"❌ Error getting existing Google Calendar events: {str(e)}")
            return []
    
    def sync_to_google_calendar(self, subsplash_events):
        """Sync Subsplash events to Google Calendar"""
        try:
            if not self.calendar_service:
                print("❌ Google Calendar service not initialized")
                return False
            
            # Get date range for existing events
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now() + timedelta(days=365)
            
            existing_events = self.get_existing_google_events(start_date, end_date)
            
            # Create a map of existing events by title and start time
            existing_event_map = {}
            for event in existing_events:
                if 'start' in event and 'dateTime' in event['start']:
                    start_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                    key = f"{event['summary']}_{start_time.strftime('%Y%m%d_%H%M')}"
                    existing_event_map[key] = event
            
            synced_count = 0
            updated_count = 0
            
            for event_data in subsplash_events:
                # Create event key for comparison
                event_key = f"{event_data['title']}_{event_data['start'].strftime('%Y%m%d_%H%M')}"
                
                # Prepare event for Google Calendar
                google_event = {
                    'summary': event_data['title'],
                    'description': event_data.get('description', ''),
                    'location': event_data.get('location', ''),
                    'start': {
                        'dateTime': event_data['start'].isoformat(),
                        'timeZone': 'America/New_York'
                    },
                    'end': {
                        'dateTime': event_data['end'].isoformat(),
                        'timeZone': 'America/New_York'
                    }
                }
                
                if event_data.get('all_day', False):
                    google_event['start'] = {'date': event_data['start'].date().isoformat()}
                    google_event['end'] = {'date': event_data['end'].date().isoformat()}
                
                # Check if event already exists
                if event_key in existing_event_map:
                    # Update existing event
                    existing_event = existing_event_map[event_key]
                    try:
                        self.calendar_service.events().update(
                            calendarId=GOOGLE_CALENDAR_ID,
                            eventId=existing_event['id'],
                            body=google_event
                        ).execute()
                        updated_count += 1
                        print(f"🔄 Updated event: {event_data['title']}")
                    except Exception as e:
                        print(f"❌ Error updating event {event_data['title']}: {str(e)}")
                else:
                    # Create new event
                    try:
                        self.calendar_service.events().insert(
                            calendarId=GOOGLE_CALENDAR_ID,
                            body=google_event
                        ).execute()
                        synced_count += 1
                        print(f"✅ Created event: {event_data['title']}")
                    except Exception as e:
                        print(f"❌ Error creating event {event_data['title']}: {str(e)}")
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
            
            print(f"🎯 Sync complete: {synced_count} new events, {updated_count} updated events")
            return True
            
        except Exception as e:
            print(f"❌ Error syncing to Google Calendar: {str(e)}")
            return False
    
    def save_status(self, success, message):
        """Save sync status for GitHub Actions to commit"""
        status = {
            'last_sync': datetime.now().isoformat(),
            'success': success,
            'message': message,
            'calendar_id': GOOGLE_CALENDAR_ID,
            'subsplash_url': SUBSPLASH_EMBED_URL
        }
        
        with open('sync_status.json', 'w') as f:
            json.dump(status, f, indent=2)
        
        print(f"📝 Status saved: {message}")
    
    def run_sync(self):
        """Main sync method"""
        print("�� Starting Subsplash to Google Calendar sync...")
        print(f"�� Target Calendar ID: {GOOGLE_CALENDAR_ID}")
        print(f"🔗 Subsplash URL: {SUBSPLASH_EMBED_URL}")
        
        # Authenticate with Google
        if not self.authenticate_google():
            self.save_status(False, "Google authentication failed")
            return False
        
        # Scrape Subsplash events
        subsplash_events = self.scrape_subsplash_events()
        if not subsplash_events:
            self.save_status(False, "No events found from Subsplash")
            return False
        
        # Sync to Google Calendar
        if self.sync_to_google_calendar(subsplash_events):
            self.save_status(True, f"Successfully synced {len(subsplash_events)} events")
            return True
        else:
            self.save_status(False, "Sync to Google Calendar failed")
            return False

def main():
    """Main function for GitHub Actions"""
    if not GOOGLE_CALENDAR_ID or not SUBSPLASH_EMBED_URL:
        print("❌ Missing required environment variables")
        print(f"GOOGLE_CALENDAR_ID: {GOOGLE_CALENDAR_ID}")
        print(f"SUBSPLASH_EMBED_URL: {SUBSPLASH_EMBED_URL}")
        exit(1)
    
    service = SubsplashSyncService()
    success = service.run_sync()
    
    if success:
        print("🎉 Sync completed successfully!")
        exit(0)
    else:
        print("💥 Sync failed!")
        exit(1)

if __name__ == "__main__":
    main()