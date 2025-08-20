#!/usr/bin/env python3
"""
Test script to verify calendar ID loading and configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
print("🔍 Testing Calendar ID Configuration")
print("=" * 50)

# Check each calendar ID
calendars = {
    'BAM': 'BAM_CALENDAR_ID',
    'Kingdom Kids': 'KIDS_CALENDAR_ID', 
    'Prayer': 'PRAYER_CALENDAR_ID'
}

for calendar_name, env_var in calendars.items():
    calendar_id = os.environ.get(env_var)
    if calendar_id:
        print(f"✅ {calendar_name}: {calendar_id}")
    else:
        print(f"❌ {calendar_name}: Environment variable {env_var} not found")

print("\n🔍 Checking CALENDAR_CONFIG fallbacks...")
print("=" * 50)

# Import the config from sync_script
try:
    from sync_script import CALENDAR_CONFIG
    
    for calendar_key, calendar_config in CALENDAR_CONFIG.items():
        calendar_id = calendar_config['google_calendar_id']
        calendar_name = calendar_config['name']
        print(f"📅 {calendar_name} ({calendar_key}): {calendar_id}")
        
except Exception as e:
    print(f"❌ Error importing CALENDAR_CONFIG: {str(e)}")

print("\n🔍 Environment variable summary:")
print("=" * 50)
print(f"BAM_CALENDAR_ID: {os.environ.get('BAM_CALENDAR_ID', 'NOT SET')}")
print(f"KIDS_CALENDAR_ID: {os.environ.get('KIDS_CALENDAR_ID', 'NOT SET')}")
print(f"PRAYER_CALENDAR_ID: {os.environ.get('PRAYER_CALENDAR_ID', 'NOT SET')}")
print(f"GOOGLE_CALENDAR_ID: {os.environ.get('GOOGLE_CALENDAR_ID', 'NOT SET')}")
