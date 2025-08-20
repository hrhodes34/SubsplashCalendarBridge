#!/usr/bin/env python3
"""
Subsplash Calendar Bridge - Flask Backend
Automatically syncs Subsplash calendar events to Google Calendar
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
from bs4 import BeautifulSoup
import schedule
import time
import threading
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Configuration
SCOPES = ['https://www.googleapis.com/auth/calendar']
GOOGLE_CALENDAR_ID = 'b878d99dde022f1b50ebeed8cef2b7ecc77e8b6a14cce053bad48555cd697c83@group.calendar.google.com'
SUBSPLASH_EMBED_URL = '+wrmm/lb/ca/+pysr4r6?embed'  # Update with your actual Subsplash embed URL
SYNC_INTERVAL_HOURS = 6

# Global variables
credentials = None
calendar_service = None
last_sync_time = None
sync_status = 'idle'

class SubsplashCalendarBridge:
    def __init__(self):
        self.calendar_service = None
        self.credentials = None
        
    def authenticate_google(self):
        """Authenticate with Google Calendar API"""
        global credentials, calendar_service
        
        try:
            # For testing purposes, skip authentication for now
            logger.info("Skipping Google authentication for testing")
            return True
            
            # TODO: Implement proper Google authentication
            # Check if we have valid credentials
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            elif not credentials:
                # Load credentials from file
                if os.path.exists('token.json'):
                    credentials = Credentials.from_authorized_user_file('token.json', SCOPES)
                else:
                    # First time setup - need to create credentials.json
                    if not os.path.exists('credentials.json'):
                        logger.error("credentials.json not found. Please download from Google Cloud Console")
                        return False
                    
                    # Use the correct method for the installed version
                    try:
                        flow = InstalledAppFlow.from_client_secret_file('credentials.json', SCOPES)
                    except AttributeError:
                        # Fallback for older versions
                        from google_auth_oauthlib.flow import Flow
                        flow = Flow.from_client_secrets_file('credentials.json', SCOPES)
                        flow.redirect_uri = 'http://localhost:8080'
                    
                    credentials = flow.run_local_server(port=0)
                    
                    # Save credentials for next run
                    with open('token.json', 'w') as token:
                        token.write(credentials.to_json())
            
            # Build the service
            calendar_service = build('calendar', 'v3', credentials=credentials)
            logger.info("Google Calendar authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Google Calendar authentication failed: {e}")
            return False
    
    def scrape_subsplash_events(self):
        """Scrape events from Subsplash calendar"""
        try:
            # This is a placeholder - you'll need to implement actual Subsplash scraping
            # based on your specific Subsplash setup
            logger.info("Scraping Subsplash calendar...")
            
            # For now, return sample events - replace with actual Subsplash scraping
            sample_events = [
                {
                    'title': 'Sunday Service',
                    'start': datetime.now().replace(hour=10, minute=0, second=0, microsecond=0),
                    'end': datetime.now().replace(hour=11, minute=30, second=0, microsecond=0),
                    'description': 'Weekly Sunday service',
                    'location': 'Main Sanctuary'
                },
                {
                    'title': 'Bible Study',
                    'start': (datetime.now() + timedelta(days=2)).replace(hour=19, minute=0, second=0, microsecond=0),
                    'end': (datetime.now() + timedelta(days=2)).replace(hour=20, minute=30, second=0, microsecond=0),
                    'description': 'Weekly Bible study group',
                    'location': 'Fellowship Hall'
                }
            ]
            
            logger.info(f"Scraped {len(sample_events)} events from Subsplash")
            return sample_events
            
        except Exception as e:
            logger.error(f"Error scraping Subsplash events: {e}")
            return []
    
    def sync_to_google_calendar(self, events):
        """Sync events to Google Calendar"""
        global calendar_service
        
        if not calendar_service:
            logger.error("Google Calendar service not initialized")
            return False
        
        try:
            synced_count = 0
            updated_count = 0
            
            for event in events:
                # Check if event already exists
                existing_events = calendar_service.events().list(
                    calendarId=GOOGLE_CALENDAR_ID,
                    q=event['title'],
                    timeMin=event['start'].isoformat() + 'Z',
                    timeMax=event['end'].isoformat() + 'Z'
                ).execute()
                
                event_body = {
                    'summary': event['title'],
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'start': {
                        'dateTime': event['start'].isoformat(),
                        'timeZone': 'America/New_York'
                    },
                    'end': {
                        'dateTime': event['end'].isoformat(),
                        'timeZone': 'America/New_York'
                    }
                }
                
                if existing_events['items']:
                    # Update existing event
                    event_id = existing_events['items'][0]['id']
                    calendar_service.events().update(
                        calendarId=GOOGLE_CALENDAR_ID,
                        eventId=event_id,
                        body=event_body
                    ).execute()
                    updated_count += 1
                else:
                    # Create new event
                    calendar_service.events().insert(
                        calendarId=GOOGLE_CALENDAR_ID,
                        body=event_body
                    ).execute()
                    synced_count += 1
            
            logger.info(f"Sync completed: {synced_count} new events, {updated_count} updated")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing to Google Calendar: {e}")
            return False
    
    def run_sync(self):
        """Run the complete sync process"""
        global last_sync_time, sync_status
        
        try:
            sync_status = 'syncing'
            last_sync_time = datetime.now()
            
            # Authenticate if needed
            if not self.authenticate_google():
                sync_status = 'error'
                return False
            
            # Scrape Subsplash events
            events = self.scrape_subsplash_events()
            if not events:
                logger.warning("No events found to sync")
                sync_status = 'idle'
                return False
            
            # Sync to Google Calendar
            success = self.sync_to_google_calendar(events)
            sync_status = 'success' if success else 'error'
            
            return success
            
        except Exception as e:
            logger.error(f"Sync process failed: {e}")
            sync_status = 'error'
            return False

# Initialize the bridge
bridge = SubsplashCalendarBridge()

def run_scheduled_sync():
    """Run sync on schedule"""
    while True:
        try:
            bridge.run_sync()
            time.sleep(SYNC_INTERVAL_HOURS * 3600)  # Convert hours to seconds
        except Exception as e:
            logger.error(f"Scheduled sync error: {e}")
            time.sleep(3600)  # Wait 1 hour on error

# Start scheduled sync in background thread
sync_thread = threading.Thread(target=run_scheduled_sync, daemon=True)
sync_thread.start()

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/widget/weekly')
def weekly_widget():
    """Weekly calendar widget"""
    return render_template('widget.html')

@app.route('/widget/monthly')
def monthly_widget():
    """Monthly calendar widget"""
    return render_template('widget.html')

@app.route('/widget/quarterly')
def quarterly_widget():
    """Quarterly calendar widget"""
    return render_template('widget.html')

@app.route('/widget/annually')
def annually_widget():
    """Annual calendar widget"""
    return render_template('widget.html')

@app.route('/api/calendar/events')
def get_calendar_events():
    """API endpoint to get calendar events"""
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        
        if not start_date or not end_date:
            return jsonify({'success': False, 'message': 'Start and end dates required'})
        
        # For testing, return sample events
        sample_events = [
            {
                'id': '1',
                'title': 'Sunday Service',
                'start': datetime.now().replace(hour=10, minute=0, second=0, microsecond=0).isoformat(),
                'end': datetime.now().replace(hour=11, minute=30, second=0, microsecond=0).isoformat(),
                'description': 'Weekly Sunday service',
                'location': 'Main Sanctuary',
                'allDay': False,
                'backgroundColor': '#007bff',
                'borderColor': '#007bff'
            },
            {
                'id': '2',
                'title': 'Bible Study',
                'start': (datetime.now() + timedelta(days=2)).replace(hour=19, minute=0, second=0, microsecond=0).isoformat(),
                'end': (datetime.now() + timedelta(days=2)).replace(hour=20, minute=30, second=0, microsecond=0).isoformat(),
                'description': 'Weekly Bible study group',
                'location': 'Fellowship Hall',
                'allDay': False,
                'backgroundColor': '#28a745',
                'borderColor': '#28a745'
            },
            {
                'id': '3',
                'title': 'Youth Group',
                'start': (datetime.now() + timedelta(days=4)).replace(hour=18, minute=0, second=0, microsecond=0).isoformat(),
                'end': (datetime.now() + timedelta(days=4)).replace(hour=20, minute=0, second=0, microsecond=0).isoformat(),
                'description': 'Youth group meeting and activities',
                'location': 'Youth Center',
                'allDay': False,
                'backgroundColor': '#ffc107',
                'borderColor': '#ffc107'
            }
        ]
        
        return jsonify({'success': True, 'events': sample_events})
        
        # TODO: Implement actual Google Calendar integration
        # Authenticate if needed
        # if not bridge.authenticate_google():
        #     return jsonify({'success': False, 'message': 'Authentication failed'})
        
        # # Get events from Google Calendar
        # events = bridge.calendar_service.events().list(
        #     calendarId=GOOGLE_CALENDAR_ID,
        #     timeMin=start_date,
        #     timeMax=end_date,
        #     singleEvents=True,
        #     orderBy='startTime'
        # ).execute()
        
        # # Format events for FullCalendar
        # formatted_events = []
        # for event in events.get('items', []):
        #     formatted_events.append({
        #         'id': event['id'],
        #         'title': event.get('summary', 'No Title'),
        #         'start': event['start'].get('dateTime', event['start'].get('date')),
        #         'end': event['end'].get('dateTime', event['end'].get('date')),
        #         'description': event.get('description', ''),
        #         'location': event.get('location', ''),
        #         'allDay': 'date' in event['start'],
        #         'backgroundColor': '#007bff',
        #         'borderColor': '#007bff'
        #     })
        
        # return jsonify({'success': True, 'events': formatted_events})
        
    except Exception as e:
        logger.error(f"Error getting calendar events: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/sync/status')
def get_sync_status():
    """Get current sync status"""
    return jsonify({
        'status': sync_status,
        'last_sync': last_sync_time.isoformat() if last_sync_time else None,
        'next_sync': (last_sync_time + timedelta(hours=SYNC_INTERVAL_HOURS)).isoformat() if last_sync_time else None
    })

@app.route('/api/sync/trigger', methods=['POST'])
def trigger_sync():
    """Manually trigger a sync"""
    try:
        success = bridge.run_sync()
        return jsonify({'success': success, 'message': 'Sync completed' if success else 'Sync failed'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    # Run initial sync
    logger.info("Starting Subsplash Calendar Bridge...")
    bridge.run_sync()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)