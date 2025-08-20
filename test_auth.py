#!/usr/bin/env python3
"""
Test script to verify Google Calendar API authentication
and access to all configured calendars.
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from sync_script import CALENDAR_CONFIG

def test_calendar_access():
    """Test access to all configured calendars."""
    
    # Check if credentials file exists
    credentials_path = 'credentials.json'
    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        print("Please ensure you have credentials.json in your directory")
        return False
    
    try:
        # Load credentials
        print("🔐 Loading service account credentials...")
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        # Build service
        service = build('calendar', 'v3', credentials=credentials)
        print("✅ Service account authenticated successfully")
        
        # Test access to each calendar
        for calendar_key, calendar_info in CALENDAR_CONFIG.items():
            calendar_id = calendar_info['google_calendar_id']
            calendar_name = calendar_info['name']
            
            print(f"\n📅 Testing access to {calendar_name} ({calendar_key})...")
            
            try:
                # Try to get calendar details
                calendar = service.calendars().get(calendarId=calendar_id).execute()
                print(f"   ✅ Access granted to: {calendar.get('summary', 'Unknown')}")
                print(f"   📍 Calendar ID: {calendar_id}")
                
                # Try to list events (just first few to test access)
                events = service.events().list(
                    calendarId=calendar_id,
                    maxResults=3,
                    timeMin='2024-01-01T00:00:00Z'
                ).execute()
                
                event_count = len(events.get('items', []))
                print(f"   📊 Can read events: {event_count} events found")
                
            except Exception as e:
                print(f"   ❌ Access denied: {str(e)}")
                return False
        
        print("\n🎉 All calendar access tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Google Calendar API Authentication")
    print("=" * 50)
    
    success = test_calendar_access()
    
    if success:
        print("\n✅ Your authentication is working correctly!")
        print("You can now run the full sync script for all calendars.")
    else:
        print("\n❌ Authentication test failed.")
        print("Please check your credentials.json file and calendar permissions.")
