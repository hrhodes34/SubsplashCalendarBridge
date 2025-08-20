#!/usr/bin/env python3
"""
Token Generation Script for SubsplashCalendarBridge
This script generates a new OAuth token.pickle file locally.
Run this script locally (not in GitHub Actions) to generate a fresh token.
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# OAuth 2.0 scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

def generate_oauth_token():
    """Generate a new OAuth token and save it as token.pickle"""
    
    print("🔑 Generating new OAuth token for Google Calendar API...")
    
    # Check if credentials.json exists
    credentials_file = 'credentials.json'
    if not os.path.exists(credentials_file):
        print(f"❌ {credentials_file} not found!")
        print("Please place your credentials.json file in this directory first.")
        return False
    
    try:
        # Start OAuth 2.0 flow
        print("🚀 Starting OAuth 2.0 authentication flow...")
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
        
        # This will open a browser window for authentication
        print("🌐 Opening browser for Google authentication...")
        print("Please complete the authentication in your browser.")
        
        creds = flow.run_local_server(port=0)
        
        # Save the credentials
        print("💾 Saving OAuth token to token.pickle...")
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        
        print("✅ Successfully generated and saved token.pickle!")
        print("\n📋 Next steps:")
        print("1. Copy the token.pickle file content")
        print("2. Go to GitHub repository → Settings → Secrets → Actions")
        print("3. Create/update GOOGLE_TOKEN secret with the token.pickle content")
        print("4. Delete the local token.pickle file for security")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate token: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("SubsplashCalendarBridge - OAuth Token Generator")
    print("=" * 60)
    
    success = generate_oauth_token()
    
    if success:
        print("\n🎉 Token generation completed successfully!")
    else:
        print("\n💥 Token generation failed. Please check the error above.")
