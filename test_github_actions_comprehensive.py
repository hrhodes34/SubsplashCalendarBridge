#!/usr/bin/env python3
"""
Comprehensive GitHub Actions Test Script
This script simulates the exact GitHub Actions environment and tests the full sync functionality
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

def test_environment_simulation():
    """Test environment variables and configuration"""
    logger.info("🔧 Testing GitHub Actions environment simulation...")
    
    # Set GitHub Actions environment
    os.environ['GITHUB_ACTIONS'] = 'true'
    os.environ['SAVE_DEBUG_FILES'] = 'true'
    os.environ['VERBOSE_DEBUG'] = 'true'
    os.environ['BROWSER_WAIT_TIME'] = '15'
    
    # Test calendar IDs (using test values)
    test_calendar_ids = {
        'PRAYER_CALENDAR_ID': 'test_prayer_id',
        'BAM_CALENDAR_ID': 'test_bam_id',
        'KIDS_CALENDAR_ID': 'test_kids_id'
    }
    
    for key, value in test_calendar_ids.items():
        os.environ[key] = value
        logger.info(f"✅ Set {key} = {value}")
    
    logger.info("✅ Environment simulation complete")
    return True

def test_browser_setup_simulation():
    """Test browser setup with GitHub Actions simulation"""
    logger.info("🌐 Testing browser setup simulation...")
    
    try:
        # Import after environment setup
        from sync_script import SubsplashCalendarSync
        
        # Create sync instance
        sync = SubsplashCalendarSync()
        logger.info("✅ Sync instance created successfully")
        
        # Test browser setup
        logger.info("🧪 Testing browser setup...")
        browser_success = sync.setup_browser()
        
        if browser_success:
            logger.info("✅ Browser setup successful")
            
            # Test page loading
            logger.info("🧪 Testing page loading...")
            try:
                sync.browser.get('https://antiochboone.com/calendar-prayer')
                time.sleep(5)
                
                # Check if page loaded
                page_title = sync.browser.title
                logger.info(f"📄 Page title: {page_title}")
                
                # Check for calendar elements
                calendar_elements = sync.browser.find_elements('class name', "fc-toolbar-title")
                if calendar_elements:
                    logger.info(f"✅ Calendar toolbar found: {len(calendar_elements)} elements")
                    for elem in calendar_elements:
                        logger.info(f"   - {elem.text}")
                else:
                    logger.warning("⚠️ Calendar toolbar not found")
                
                # Check for events
                event_elements = sync.browser.find_elements('class name', "fc-event")
                logger.info(f"📅 Event elements found: {len(event_elements)}")
                
                # Save page source for debugging
                if sync.save_debug_files:
                    debug_file = f"comprehensive_test_page_source_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(sync.browser.page_source)
                    logger.info(f"💾 Page source saved to {debug_file}")
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Page loading failed: {str(e)}")
                return False
            finally:
                if sync.browser:
                    sync.browser.quit()
                    logger.info("🧹 Browser cleaned up")
        else:
            logger.error("❌ Browser setup failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Browser setup simulation failed: {str(e)}")
        return False

def test_calendar_scraping_simulation():
    """Test calendar scraping functionality"""
    logger.info("📅 Testing calendar scraping simulation...")
    
    try:
        from sync_script import SubsplashCalendarSync
        
        # Create sync instance
        sync = SubsplashCalendarSync()
        
        # Test scraping a single calendar
        logger.info("🧪 Testing prayer calendar scraping...")
        events = sync.scrape_calendar_events('prayer')
        
        if events:
            logger.info(f"✅ Successfully scraped {len(events)} events")
            
            # Save events for debugging
            if sync.save_debug_files:
                debug_file = f"comprehensive_test_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    json.dump(events, f, indent=2, default=str)
                logger.info(f"💾 Events saved to {debug_file}")
            
            # Display event details
            for i, event in enumerate(events[:3]):  # Show first 3 events
                logger.info(f"   Event {i+1}: {event.get('title', 'No title')} on {event.get('date', 'No date')}")
            
            return True
        else:
            logger.warning("⚠️ No events scraped")
            return False
            
    except Exception as e:
        logger.error(f"❌ Calendar scraping simulation failed: {str(e)}")
        return False

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    logger.info("🚀 Starting comprehensive GitHub Actions simulation tests...")
    
    tests = [
        ("Environment Simulation", test_environment_simulation),
        ("Browser Setup Simulation", test_browser_setup_simulation),
        ("Calendar Scraping Simulation", test_calendar_scraping_simulation)
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running test: {test_name}")
        try:
            results[test_name] = test_func()
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            logger.info(f"{status} - {test_name}")
        except Exception as e:
            results[test_name] = False
            logger.error(f"❌ FAIL - {test_name}: {str(e)}")
    
    # Summary
    logger.info("\n📊 Comprehensive Test Results Summary:")
    passed = sum(results.values())
    total = len(results)
    logger.info(f"Passed: {passed}/{total}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {status} - {test_name}")
    
    # Recommendations
    logger.info("\n💡 Recommendations for GitHub Actions:")
    if results["Browser Setup Simulation"]:
        logger.info("✅ Browser setup should work in GitHub Actions")
    else:
        logger.info("❌ Browser setup may fail in GitHub Actions - check Chrome installation")
    
    if results["Calendar Scraping Simulation"]:
        logger.info("✅ Calendar scraping should work in GitHub Actions")
    else:
        logger.info("❌ Calendar scraping may fail in GitHub Actions - check page loading")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_tests()
    
    if success:
        logger.info("🎉 All comprehensive tests passed! GitHub Actions should work well.")
        exit(0)
    else:
        logger.error("💥 Some comprehensive tests failed. Check the logs above for issues.")
        exit(1)
