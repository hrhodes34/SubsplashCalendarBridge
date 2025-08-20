#!/usr/bin/env python3
"""
Test script for the multi-calendar system
This demonstrates how to use the new calendar configuration
"""

import os
from sync_script import (
    CALENDAR_CONFIG, 
    get_enabled_calendars, 
    get_calendar_by_name,
    export_calendar_config_for_frontend,
    get_calendar_urls
)

def test_calendar_configuration():
    """Test the calendar configuration system"""
    print("🧪 Testing Multi-Calendar Configuration System")
    print("=" * 60)
    
    # Display all configured calendars
    print("\n📅 All Configured Calendars:")
    for calendar_key, calendar_config in CALENDAR_CONFIG.items():
        status = "✅ Enabled" if calendar_config['enabled'] else "❌ Disabled"
        calendar_id = calendar_config['google_calendar_id'] or "Not configured"
        print(f"   • {calendar_config['name']} ({calendar_key})")
        print(f"     Status: {status}")
        print(f"     URL: {calendar_config['subsplash_url']}")
        print(f"     Google Calendar ID: {calendar_id}")
        print(f"     Color: {calendar_config['color']}")
        print()
    
    # Show enabled calendars only
    print("\n🎯 Enabled Calendars Only:")
    enabled_calendars = get_enabled_calendars()
    for calendar_key, calendar_config in enabled_calendars.items():
        print(f"   • {calendar_config['name']} ({calendar_key})")
    
    # Test getting a specific calendar
    print("\n🔍 Testing Calendar Lookup:")
    youth_calendar = get_calendar_by_name('youth')
    if youth_calendar:
        print(f"   Found Youth calendar: {youth_calendar['name']}")
    else:
        print("   Youth calendar not found")
    
    # Test frontend export
    print("\n🌐 Frontend Configuration Export:")
    frontend_config = export_calendar_config_for_frontend()
    print("   Frontend-ready config:")
    for key, config in frontend_config.items():
        print(f"     {key}: {config}")
    
    # Test URL export
    print("\n🔗 Calendar URLs for Frontend:")
    urls = get_calendar_urls()
    for key, url_info in urls.items():
        print(f"   {key}: {url_info['name']} - {url_info['url']}")
    
    # Environment variable check
    print("\n🔧 Environment Variable Status:")
    for calendar_key in CALENDAR_CONFIG.keys():
        env_var = f"{calendar_key.upper()}_CALENDAR_ID"
        value = os.environ.get(env_var, "Not set")
        print(f"   {env_var}: {value}")

def test_calendar_creation():
    """Test creating a SubsplashSyncService instance for a specific calendar"""
    print("\n🧪 Testing Calendar Service Creation:")
    print("=" * 60)
    
    try:
        from sync_script import SubsplashSyncService
        
        # Test with youth calendar
        youth_calendar = get_calendar_by_name('youth')
        if youth_calendar:
            print(f"   Creating service for {youth_calendar['name']}...")
            # Note: This won't actually authenticate, just test the initialization
            service = SubsplashSyncService(youth_calendar)
            print(f"   ✅ Service created successfully for {service.target_calendar['name']}")
        else:
            print("   ❌ Youth calendar not found")
            
    except Exception as e:
        print(f"   ⚠️ Service creation test failed: {str(e)}")
        print("   (This is expected if credentials aren't configured)")

if __name__ == "__main__":
    test_calendar_configuration()
    test_calendar_creation()
    
    print("\n🎉 Multi-calendar system test completed!")
    print("\n💡 To use this system:")
    print("   1. Copy config.env.example to .env")
    print("   2. Set your Google Calendar IDs for each ministry")
    print("   3. Run sync_script.py to sync all calendars")
    print("   4. Use export_calendar_config_for_frontend() for FullCalendar integration")
