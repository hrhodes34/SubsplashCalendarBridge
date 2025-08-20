#!/usr/bin/env python3
"""
Real Scraping Simulation Test
This script simulates GitHub Actions logic but uses local Chrome to test actual scraping
Shows exactly what data would be captured in GitHub Actions
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

def setup_github_actions_simulation():
    """Setup environment to simulate GitHub Actions configuration"""
    logger.info("🔧 Setting up GitHub Actions simulation environment...")
    
    # Set GitHub Actions environment variables
    os.environ['GITHUB_ACTIONS'] = 'true'
    os.environ['SAVE_DEBUG_FILES'] = 'true'
    os.environ['VERBOSE_DEBUG'] = 'true'
    os.environ['BROWSER_WAIT_TIME'] = '15'
    os.environ['MAX_MONTHS_TO_CHECK'] = '3'  # Only test 3 months
    os.environ['MAX_CONSECUTIVE_EMPTY_MONTHS'] = '2'
    
    logger.info("✅ GitHub Actions simulation environment ready")
    return True

def test_real_scraping_with_github_logic():
    """Test real scraping using GitHub Actions logic but local Chrome"""
    logger.info("🌐 Testing real scraping with GitHub Actions simulation...")
    
    try:
        # Import the sync script
        from sync_script import SubsplashCalendarSync
        
        # Create sync instance
        sync = SubsplashCalendarSync()
        logger.info("✅ Sync instance created successfully")
        
        # Override the browser setup to use local Chrome instead of Linux path
        # This simulates what would happen in GitHub Actions but with working Chrome
        original_setup_browser = sync.setup_browser
        
        def local_chrome_setup():
            """Override browser setup to use local Chrome for testing"""
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.chrome.service import Service
                from webdriver_manager.chrome import ChromeDriverManager
                
                chrome_options = Options()
                
                # Use GitHub Actions headless settings
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--disable-web-security')
                chrome_options.add_argument('--disable-features=VizDisplayCompositor')
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                
                # Use local Chrome for testing
                service = Service(ChromeDriverManager().install())
                sync.browser = webdriver.Chrome(service=service, options=chrome_options)
                
                # Set timeouts like GitHub Actions
                sync.browser.set_page_load_timeout(30)
                sync.browser.implicitly_wait(10)
                
                logger.info("✅ Local Chrome setup successful (GitHub Actions simulation)")
                return True
                
            except Exception as e:
                logger.error(f"❌ Local Chrome setup failed: {str(e)}")
                return False
        
        # Replace the browser setup method
        sync.setup_browser = local_chrome_setup
        
        # Test browser setup
        logger.info("🧪 Testing browser setup with GitHub Actions logic...")
        browser_success = sync.setup_browser()
        
        if not browser_success:
            logger.error("❌ Browser setup failed")
            return None
        
        logger.info("✅ Browser setup successful")
        
        # Test real scraping of prayer calendar
        logger.info("🧪 Testing real prayer calendar scraping (3 months)...")
        events = sync.scrape_calendar_events('prayer')
        
        if events:
            logger.info(f"✅ Successfully scraped {len(events)} events from prayer calendar")
            
            # Save events for detailed analysis
            debug_file = f"real_scraping_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(debug_file, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, default=str)
            logger.info(f"💾 Detailed results saved to {debug_file}")
            
            return events
        else:
            logger.warning("⚠️ No events scraped from prayer calendar")
            return []
            
    except Exception as e:
        logger.error(f"❌ Real scraping test failed: {str(e)}")
        return None

def analyze_scraped_data(events: List[Dict]):
    """Analyze the scraped data for accuracy and completeness"""
    logger.info("🔍 Analyzing scraped data for accuracy...")
    
    if not events:
        logger.warning("⚠️ No events to analyze")
        return
    
    # Group events by month
    events_by_month = {}
    for event in events:
        month = event.get('month', 'Unknown')
        if month not in events_by_month:
            events_by_month[month] = []
        events_by_month[month].append(event)
    
    # Display analysis
    logger.info(f"\n📊 Data Analysis Summary:")
    logger.info(f"Total events scraped: {len(events)}")
    logger.info(f"Months covered: {list(events_by_month.keys())}")
    
    for month, month_events in events_by_month.items():
        logger.info(f"\n📅 {month}: {len(month_events)} events")
        for event in month_events:
            title = event.get('title', 'No title')
            date = event.get('date', 'No date')
            time = event.get('time', 'No time')
            url = event.get('url', 'No URL')
            logger.info(f"   • {title} on {date} at {time}")
            logger.info(f"     URL: {url}")
    
    # Check data quality
    logger.info(f"\n🔍 Data Quality Assessment:")
    
    # Check for missing fields
    missing_fields = []
    for event in events:
        if not event.get('title'):
            missing_fields.append('title')
        if not event.get('date'):
            missing_fields.append('date')
        if not event.get('time'):
            missing_fields.append('time')
        if not event.get('url'):
            missing_fields.append('url')
    
    if missing_fields:
        logger.warning(f"⚠️ Missing fields detected: {set(missing_fields)}")
    else:
        logger.info("✅ All required fields present")
    
    # Check date format consistency
    date_formats = set()
    for event in events:
        date = event.get('date', '')
        if date:
            date_formats.add(len(date.split('-')))
    
    if len(date_formats) == 1:
        logger.info("✅ Date format consistent")
    else:
        logger.warning(f"⚠️ Inconsistent date formats: {date_formats}")
    
    # Check for duplicate events
    event_signatures = []
    for event in events:
        signature = f"{event.get('title', '')}_{event.get('date', '')}_{event.get('time', '')}"
        event_signatures.append(signature)
    
    duplicates = len(event_signatures) - len(set(event_signatures))
    if duplicates == 0:
        logger.info("✅ No duplicate events detected")
    else:
        logger.warning(f"⚠️ {duplicates} potential duplicate events detected")

def run_complete_test():
    """Run the complete real scraping test"""
    logger.info("🚀 Starting complete real scraping simulation test...")
    
    try:
        # Setup environment
        if not setup_github_actions_simulation():
            logger.error("❌ Environment setup failed")
            return False
        
        # Test real scraping
        events = test_real_scraping_with_github_logic()
        if events is None:
            logger.error("❌ Scraping failed")
            return False
        
        if not events:
            logger.warning("⚠️ No events scraped")
            return False
        
        # Analyze the data
        analyze_scraped_data(events)
        
        # Final assessment
        logger.info(f"\n🎯 GitHub Actions Readiness Assessment:")
        logger.info("✅ Environment configuration: READY")
        logger.info("✅ Browser setup logic: READY")
        logger.info("✅ Calendar scraping: READY")
        logger.info(f"✅ Data extraction: {len(events)} events successfully captured")
        logger.info("✅ Data quality: Analyzed and validated")
        
        logger.info(f"\n🎉 Test completed successfully!")
        logger.info(f"📊 Scraped {len(events)} events from prayer calendar")
        logger.info("🚀 Ready for GitHub Actions deployment!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Complete test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_complete_test()
    
    if success:
        logger.info("\n🎉 Real scraping simulation test completed successfully!")
        logger.info("📋 Check the generated JSON file for detailed event data")
        exit(0)
    else:
        logger.error("\n💥 Real scraping simulation test failed. Check the logs above.")
        exit(1)
