import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import pickle

logger = logging.getLogger(__name__)

class GoogleCalendarSync:
    """Handles synchronization with Google Calendar"""
    
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        try:
            # The file token.pickle stores the user's access and refresh tokens,
            # and is created automatically when the authorization flow completes for the first time.
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    self.creds = pickle.load(token)
            
            # If there are no (valid) credentials available, let the user log in.
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    # Check if credentials file exists
                    credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
                    if not os.path.exists(credentials_file):
                        logger.warning(f"Credentials file {credentials_file} not found. Please set up Google Calendar API credentials.")
                        return
                    
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(self.creds, token)
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=self.creds)
            logger.info("Successfully authenticated with Google Calendar API")
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Calendar API: {str(e)}")
            raise
    
    def create_event(self, event_data: Dict) -> Optional[str]:
        """
        Create a new event in Google Calendar
        
        Args:
            event_data: Dictionary containing event information
            
        Returns:
            Event ID if successful, None otherwise
        """
        try:
            if not self.service:
                raise Exception("Not authenticated with Google Calendar API")
            
            # Prepare event for Google Calendar
            event = self._prepare_event_for_google(event_data)
            
            # Create the event
            event_result = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            logger.info(f"Event created: {event_result.get('id')}")
            return event_result.get('id')
            
        except Exception as e:
            logger.error(f"Failed to create event: {str(e)}")
            return None
    
    def update_event(self, event_id: str, event_data: Dict) -> bool:
        """
        Update an existing event in Google Calendar
        
        Args:
            event_id: ID of the event to update
            event_data: New event data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.service:
                raise Exception("Not authenticated with Google Calendar API")
            
            # Prepare event for Google Calendar
            event = self._prepare_event_for_google(event_data)
            
            # Update the event
            self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"Event updated: {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update event {event_id}: {str(e)}")
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete an event from Google Calendar
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.service:
                raise Exception("Not authenticated with Google Calendar API")
            
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"Event deleted: {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete event {event_id}: {str(e)}")
            return False
    
    def get_events(self, calendar_id: str = None, time_min: str = None, time_max: str = None) -> List[Dict]:
        """
        Get events from Google Calendar
        
        Args:
            calendar_id: Calendar ID (defaults to primary)
            time_min: Start time in ISO format
            time_max: End time in ISO format
            
        Returns:
            List of events
        """
        try:
            if not self.service:
                raise Exception("Not authenticated with Google Calendar API")
            
            calendar_id = calendar_id or self.calendar_id
            
            # Set default time range if not provided
            if not time_min:
                time_min = datetime.now().isoformat() + 'Z'
            if not time_max:
                time_max = (datetime.now() + timedelta(days=365)).isoformat() + 'Z'
            
            # Get events
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"Retrieved {len(events)} events from Google Calendar")
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to get events: {str(e)}")
            return []
    
    def get_events_for_view(self, view_type: str) -> List[Dict]:
        """
        Get events formatted for specific calendar view types
        
        Args:
            view_type: Type of view (weekly, monthly, quarterly, annually)
            
        Returns:
            Formatted events for the specified view
        """
        try:
            # Calculate time range based on view type
            now = datetime.now()
            
            if view_type == 'weekly':
                start_date = now - timedelta(days=now.weekday())
                end_date = start_date + timedelta(days=7)
            elif view_type == 'monthly':
                start_date = now.replace(day=1)
                if now.month == 12:
                    end_date = now.replace(year=now.year + 1, month=1, day=1)
                else:
                    end_date = now.replace(month=now.month + 1, day=1)
            elif view_type == 'quarterly':
                quarter = (now.month - 1) // 3
                start_month = quarter * 3 + 1
                start_date = now.replace(month=start_month, day=1)
                if start_month + 3 > 12:
                    end_date = now.replace(year=now.year + 1, month=1, day=1)
                else:
                    end_date = now.replace(month=start_month + 3, day=1)
            elif view_type == 'annually':
                start_date = now.replace(month=1, day=1)
                end_date = now.replace(year=now.year + 1, month=1, day=1)
            else:
                raise ValueError(f"Invalid view type: {view_type}")
            
            # Get events for the time range
            events = self.get_events(
                time_min=start_date.isoformat() + 'Z',
                time_max=end_date.isoformat() + 'Z'
            )
            
            # Format events for the view
            formatted_events = []
            for event in events:
                formatted_event = self._format_event_for_view(event, view_type)
                if formatted_event:
                    formatted_events.append(formatted_event)
            
            return formatted_events
            
        except Exception as e:
            logger.error(f"Failed to get events for {view_type} view: {str(e)}")
            return []
    
    def sync_events(self, events: List[Dict]) -> Dict:
        """
        Sync events from Subsplash to Google Calendar with comprehensive duplicate detection
        
        Args:
            events: List of events from Subsplash
            
        Returns:
            Dictionary with sync results
        """
        try:
            if not self.service:
                raise Exception("Not authenticated with Google Calendar API")
            
            results = {
                'created': 0,
                'updated': 0,
                'skipped': 0,
                'deleted': 0,
                'errors': 0,
                'details': []
            }
            
            # Get existing events from Google Calendar for the relevant date range
            # Calculate date range based on events being synced
            if events:
                event_dates = []
                for event in events:
                    start = event.get('start')
                    if start:
                        try:
                            if isinstance(start, str):
                                event_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                            else:
                                event_dt = start
                            event_dates.append(event_dt)
                        except:
                            continue
                
                if event_dates:
                    min_date = min(event_dates)
                    max_date = max(event_dates)
                    # Add some buffer to the date range
                    time_min = (min_date - timedelta(days=1)).isoformat() + 'Z'
                    time_max = (max_date + timedelta(days=1)).isoformat() + 'Z'
                else:
                    # Default to next year if we can't determine date range
                    time_min = datetime.now().isoformat() + 'Z'
                    time_max = (datetime.now() + timedelta(days=365)).isoformat() + 'Z'
            else:
                # No events to sync
                time_min = datetime.now().isoformat() + 'Z'
                time_max = (datetime.now() + timedelta(days=365)).isoformat() + 'Z'
            
            logger.info(f"Fetching existing Google Calendar events from {time_min} to {time_max}")
            existing_events = self.get_events(time_min=time_min, time_max=time_max)
            logger.info(f"Found {len(existing_events)} existing events in Google Calendar")
            
            # Process each event with comprehensive duplicate detection
            for event_data in events:
                try:
                    event_title = event_data.get('title', '')
                    
                    # Check for duplicates using comprehensive comparison
                    if self._is_duplicate_event(event_data, existing_events):
                        results['skipped'] += 1
                        results['details'].append({
                            'action': 'skipped',
                            'title': event_title,
                            'reason': 'Duplicate event already exists in Google Calendar'
                        })
                        logger.info(f"Skipping duplicate event: '{event_title}'")
                        continue
                    
                    # Create new event
                    event_id = self.create_event(event_data)
                    if event_id:
                        results['created'] += 1
                        results['details'].append({
                            'action': 'created',
                            'title': event_title,
                            'id': event_id
                        })
                        logger.info(f"Created new event: '{event_title}' (ID: {event_id})")
                    else:
                        results['errors'] += 1
                        results['details'].append({
                            'action': 'error',
                            'title': event_title,
                            'error': 'Failed to create event'
                        })
                        
                except Exception as e:
                    logger.error(f"Failed to sync event {event_data.get('title', 'Unknown')}: {str(e)}")
                    results['errors'] += 1
                    results['details'].append({
                        'action': 'error',
                        'title': event_data.get('title', 'Unknown'),
                        'error': str(e)
                    })
            
            logger.info(f"Calendar sync completed: {results['created']} created, {results['skipped']} skipped as duplicates, {results['errors']} errors")
            return results
            
        except Exception as e:
            logger.error(f"Calendar sync failed: {str(e)}")
            raise
    
    def _prepare_event_for_google(self, event_data: Dict) -> Dict:
        """Prepare event data for Google Calendar API"""
        try:
            # Extract event information
            title = event_data.get('title', 'Untitled Event')
            description = event_data.get('description', '')
            location = event_data.get('location', '')
            
            # Handle new format with start/end datetime objects
            start_datetime = event_data.get('start') or event_data.get('datetime')
            end_datetime = event_data.get('end')
            
            if not start_datetime:
                raise ValueError("Event must have a start datetime")
            
            # Convert start datetime to proper format
            if isinstance(start_datetime, str):
                start_datetime = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
            
            # Handle end datetime
            if end_datetime:
                if isinstance(end_datetime, str):
                    end_datetime = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
            else:
                # Set end time to 1 hour after start if not specified
                end_datetime = start_datetime + timedelta(hours=1)
            
            # Check if this is an all-day event (no specific time component)
            is_all_day = (start_datetime.hour == 0 and start_datetime.minute == 0 and 
                         end_datetime.hour == 0 and end_datetime.minute == 0 and
                         (end_datetime - start_datetime) >= timedelta(hours=23))
            
            # Format for Google Calendar
            if is_all_day:
                event = {
                    'summary': title,
                    'description': description,
                    'location': location,
                    'start': {
                        'date': start_datetime.date().isoformat(),
                    },
                    'end': {
                        'date': end_datetime.date().isoformat(),
                    },
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 24 * 60},
                        ],
                    },
                }
            else:
                event = {
                    'summary': title,
                    'description': description,
                    'location': location,
                    'start': {
                        'dateTime': start_datetime.isoformat(),
                        'timeZone': 'America/New_York',  # Adjust timezone as needed
                    },
                    'end': {
                        'dateTime': end_datetime.isoformat(),
                        'timeZone': 'America/New_York',  # Adjust timezone as needed
                    },
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 24 * 60},
                            {'method': 'popup', 'minutes': 30},
                        ],
                    },
                }
            
            return event
            
        except Exception as e:
            logger.error(f"Failed to prepare event for Google Calendar: {str(e)}")
            raise
    
    def _format_event_for_view(self, event: Dict, view_type: str) -> Optional[Dict]:
        """Format event for specific calendar view"""
        try:
            # Extract start and end times
            start = event.get('start', {})
            end = event.get('end', {})
            
            start_time = start.get('dateTime') or start.get('date')
            end_time = end.get('dateTime') or end.get('date')
            
            if not start_time:
                return None
            
            # Parse datetime
            if 'T' in start_time:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00')) if end_time else start_dt + timedelta(hours=1)
            else:
                start_dt = datetime.fromisoformat(start_time)
                end_dt = datetime.fromisoformat(end_time) if end_time else start_dt + timedelta(days=1)
            
            formatted_event = {
                'id': event.get('id'),
                'title': event.get('summary', 'Untitled'),
                'description': event.get('description', ''),
                'location': event.get('location', ''),
                'start': start_dt.isoformat(),
                'end': end_dt.isoformat(),
                'all_day': 'date' in start,
                'html_link': event.get('htmlLink', ''),
                'view_type': view_type
            }
            
            return formatted_event
            
        except Exception as e:
            logger.error(f"Failed to format event for view: {str(e)}")
            return None
    
    def _is_duplicate_event(self, new_event: Dict, existing_events: List[Dict]) -> bool:
        """
        Enhanced duplicate detection that handles various edge cases including all-day events
        
        Args:
            new_event: New event to check
            existing_events: List of existing Google Calendar events
            
        Returns:
            True if the event is a duplicate, False otherwise
        """
        try:
            # Get new event details
            new_title = new_event.get('title', '').strip().lower()
            new_start = new_event.get('start')
            new_end = new_event.get('end')
            
            if not new_title or not new_start:
                return False
            
            # Convert new event start time to datetime if it's a string
            if isinstance(new_start, str):
                try:
                    new_start_dt = datetime.fromisoformat(new_start.replace('Z', '+00:00'))
                except ValueError:
                    # Try parsing without timezone info
                    new_start_dt = datetime.fromisoformat(new_start.split('+')[0].split('Z')[0])
            elif hasattr(new_start, 'date'):
                new_start_dt = new_start
            else:
                return False
            
            # Check against existing events
            for existing_event in existing_events:
                existing_title = existing_event.get('summary', '').strip().lower()
                
                # Skip if titles don't match
                if new_title != existing_title:
                    continue
                
                # Get existing event start and end times
                existing_start = existing_event.get('start', {})
                existing_end = existing_event.get('end', {})
                
                existing_start_time = existing_start.get('dateTime') or existing_start.get('date')
                existing_end_time = existing_end.get('dateTime') or existing_end.get('date')
                
                if not existing_start_time:
                    continue
                
                try:
                    # Parse existing event start time
                    if 'T' in existing_start_time:
                        # Regular event with time
                        existing_start_dt = datetime.fromisoformat(existing_start_time.replace('Z', '+00:00'))
                        
                        # Check if this is a regular event (not all-day)
                        if not new_event.get('all_day', False):
                            # Compare times with 5-minute tolerance for slight variations
                            start_diff = abs((new_start_dt - existing_start_dt).total_seconds())
                            if start_diff < 300:  # 5 minutes tolerance
                                logger.info(f"Duplicate event found: '{new_title}' on {new_start_dt.strftime('%Y-%m-%d %H:%M')}")
                                return True
                    else:
                        # All-day event
                        existing_start_date = datetime.fromisoformat(existing_start_time).date()
                        
                        # Check if new event is also all-day
                        if new_event.get('all_day', False):
                            new_start_date = new_start_dt.date()
                            if new_start_date == existing_start_date:
                                logger.info(f"Duplicate all-day event found: '{new_title}' on {new_start_date}")
                                return True
                        
                except ValueError:
                    # Skip if we can't parse the existing event time
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking for duplicate event: {str(e)}")
            return False
    
    def get_calendar_info(self) -> Dict:
        """Get information about the Google Calendar"""
        try:
            if not self.service:
                raise Exception("Not authenticated with Google Calendar API")
            
            calendar = self.service.calendars().get(calendarId=self.calendar_id).execute()
            
            return {
                'id': calendar.get('id'),
                'summary': calendar.get('summary'),
                'description': calendar.get('description'),
                'timezone': calendar.get('timeZone'),
                'access_role': calendar.get('accessRole')
            }
            
        except Exception as e:
            logger.error(f"Failed to get calendar info: {str(e)}")
            return {}
