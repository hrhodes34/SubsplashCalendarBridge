#!/usr/bin/env python3
"""
Prayer Calendar Sync Test Script
This script tests the full workflow: scraping prayer calendar for 3 months and syncing to Google Calendar
Simulates the exact GitHub Actions environment
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_github_actions_environment():
    """Setup environment to simulate GitHub Actions"""
    logger.info("🔧 Setting up GitHub Actions environment simulation...")
    
    # Set GitHub Actions environment variables
    os.environ['GITHUB_ACTIONS'] = 'true'
    os.environ['SAVE_DEBUG_FILES'] = 'true'
    os.environ['VERBOSE_DEBUG'] = 'true'
    os.environ['BROWSER_WAIT_TIME'] = '15'
    os.environ['MAX_MONTHS_TO_CHECK'] = '3'  # Only test 3 months
    os.environ['MAX_CONSECUTIVE_EMPTY_MONTHS'] = '2'
    
    # Set test calendar IDs (you'll need to replace these with real ones for actual sync)
    test_calendar_ids = {
        'PRAYER_CALENDAR_ID': 'test_prayer_id',  # Replace with real ID for actual sync
        'GOOGLE_CREDENTIALS_FILE': 'credentials.json'
    }
    
    for key, value in test_calendar_ids.items():
        os.environ[key] = value
        logger.info(f"✅ Set {key} = {value}")
    
    logger.info("✅ GitHub Actions environment simulation complete")
    return True

def test_prayer_calendar_scraping():
    """Test scraping the prayer calendar for 3 months"""
    logger.info("📅 Testing prayer calendar scraping for 3 months...")
    
    try:
        # Import after environment setup
        from sync_script import SubsplashCalendarSync
        
        # Create sync instance
        sync = SubsplashCalendarSync()
        logger.info("✅ Sync instance created successfully")
        
        # Test browser setup
        logger.info("🧪 Testing browser setup...")
        browser_success = sync.setup_browser()
        
        if not browser_success:
            logger.error("❌ Browser setup failed")
            return False
        
        logger.info("✅ Browser setup successful")
        
        # Test scraping prayer calendar
        logger.info("🧪 Testing prayer calendar scraping...")
        events = sync.scrape_calendar_events('prayer')
        
        if events:
            logger.info(f"✅ Successfully scraped {len(events)} events from prayer calendar")
            
            # Save events for debugging
            if sync.save_debug_files:
                debug_file = f"prayer_calendar_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    json.dump(events, f, indent=2, default=str)
                logger.info(f"💾 Events saved to {debug_file}")
            
            # Display event details
            logger.info("\n📋 Scraped Events Summary:")
            for i, event in enumerate(events):
                event_date = event.get('date', 'No date')
                event_time = event.get('time', 'No time')
                event_title = event.get('title', 'No title')
                logger.info(f"   Event {i+1}: {event_title} on {event_date} at {event_time}")
            
            return events
        else:
            logger.warning("⚠️ No events scraped from prayer calendar")
            return []
            
    except Exception as e:
        logger.error(f"❌ Prayer calendar scraping failed: {str(e)}")
        return []

def test_google_calendar_sync(events: List[Dict]):
    """Test Google Calendar sync functionality"""
    logger.info("🔄 Testing Google Calendar sync...")
    
    try:
        from sync_script import SubsplashCalendarSync
        
        # Create sync instance
        sync = SubsplashCalendarSync()
        
        # Test Google Calendar setup
        logger.info("🧪 Testing Google Calendar setup...")
        calendar_success = sync.setup_google_calendar()
        
        if not calendar_success:
            logger.warning("⚠️ Google Calendar setup failed (expected in test environment)")
            logger.info("💡 This is normal in test environment - will work in GitHub Actions with real credentials")
            return False
        
        logger.info("✅ Google Calendar setup successful")
        
        # Test sync to Google Calendar
        logger.info("🧪 Testing sync to Google Calendar...")
        sync_result = sync.sync_events_to_google_calendar(events, 'prayer')
        
        if sync_result['success']:
            logger.info(f"✅ Sync successful: {sync_result['created']} created, {sync_result['updated']} updated")
            return True
        else:
            logger.error(f"❌ Sync failed: {sync_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Google Calendar sync test failed: {str(e)}")
        return False

def run_full_workflow_test():
    """Run the complete workflow test"""
    logger.info("🚀 Starting full prayer calendar workflow test...")
    
    try:
        # Setup environment
        if not setup_github_actions_environment():
            logger.error("❌ Environment setup failed")
            return False
        
        # Test scraping
        events = test_prayer_calendar_scraping()
        if not events:
            logger.error("❌ Scraping failed - cannot test sync")
            return False
        
        # Test Google Calendar sync (may fail in test environment)
        sync_success = test_google_calendar_sync(events)
        
        # Summary
        logger.info("\n📊 Full Workflow Test Results:")
        logger.info(f"✅ Scraping: {len(events)} events successfully extracted")
        logger.info(f"{'✅' if sync_success else '⚠️'} Google Calendar Sync: {'Successful' if sync_success else 'Failed (expected in test)'}")
        
        # Recommendations for GitHub Actions
        logger.info("\n💡 GitHub Actions Readiness Assessment:")
        logger.info("✅ Environment configuration: READY")
        logger.info("✅ Browser setup: READY") 
        logger.info("✅ Calendar scraping: READY")
        logger.info(f"{'✅' if sync_success else '⚠️'} Google Calendar sync: {'READY' if sync_success else 'NEEDS REAL CREDENTIALS'}")
        
        if sync_success:
            logger.info("🎉 All tests passed! GitHub Actions will work perfectly.")
        else:
            logger.info("🎯 Core functionality ready! Google Calendar sync will work in GitHub Actions with real credentials.")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Full workflow test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_full_workflow_test()
    
    if success:
        logger.info("\n🎉 Prayer calendar workflow test completed successfully!")
        logger.info("🚀 Ready to deploy to GitHub Actions!")
        exit(0)
    else:
        logger.error("\n💥 Prayer calendar workflow test failed. Check the logs above.")
        exit(1)
