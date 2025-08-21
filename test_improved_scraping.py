#!/usr/bin/env python3
"""
Test script for improved calendar scraping
"""

import os
import sys
import logging
from datetime import datetime

# Add the current directory to the path so we can import sync_script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sync_script import SubsplashCalendarSync

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_prayer_calendar_scraping():
    """Test scraping the prayer calendar specifically"""
    logger.info("🧪 Testing improved prayer calendar scraping...")
    
    # Create sync instance
    sync = SubsplashCalendarSync()
    
    try:
        # Test browser setup
        if not sync.setup_browser():
            logger.error("❌ Failed to setup browser")
            return
        
        # Navigate to prayer calendar
        calendar_url = sync.calendar_urls.get('prayer')
        if not calendar_url:
            logger.error("❌ No URL found for prayer calendar")
            return
        
        logger.info(f"🌐 Navigating to prayer calendar: {calendar_url}")
        sync.browser.get(calendar_url)
        
        # Wait for page to load
        import time
        time.sleep(5)
        
        # Get current month/year
        current_month, current_year = sync.get_current_month_year()
        logger.info(f"📅 Current month/year: {current_month} {current_year}")
        
        # Scrape current month events
        events = sync.scrape_current_month_events('prayer')
        logger.info(f"📝 Found {len(events)} events")
        
        # Display events
        for i, event in enumerate(events):
            logger.info(f"Event {i+1}:")
            logger.info(f"  Title: {event.get('title', 'N/A')}")
            logger.info(f"  Date: {event.get('date', 'N/A')}")
            logger.info(f"  Time: {event.get('time', 'N/A')}")
            logger.info(f"  Start: {event.get('start', 'N/A')}")
            logger.info(f"  End: {event.get('end', 'N/A')}")
            logger.info(f"  All Day: {event.get('all_day', 'N/A')}")
            logger.info("  ---")
        
        # Test weekly event detection
        if events:
            logger.info("🔍 Testing weekly event detection...")
            expanded_events = sync._detect_weekly_recurring_events(events, 'prayer')
            logger.info(f"📊 Expanded {len(events)} events to {len(expanded_events)} total events")
            
            # Show recurring events
            recurring_events = [e for e in expanded_events if e.get('recurring', False)]
            logger.info(f"🔄 Found {len(recurring_events)} recurring events")
            
            for event in recurring_events[:5]:  # Show first 5
                logger.info(f"  Recurring: {event['title']} on {event['date']} at {event['time']}")
        
        # Save results for inspection
        import json
        test_results = {
            'timestamp': datetime.now().isoformat(),
            'month': current_month,
            'year': current_year,
            'events': events,
            'expanded_events': expanded_events if events else []
        }
        
        with open('test_improved_scraping_results.json', 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        
        logger.info("💾 Test results saved to test_improved_scraping_results.json")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if sync.browser:
            sync.browser.quit()

if __name__ == "__main__":
    test_prayer_calendar_scraping()
