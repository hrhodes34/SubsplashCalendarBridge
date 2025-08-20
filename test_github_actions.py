#!/usr/bin/env python3
"""
GitHub Actions Test Script
This script tests the scraping functionality in a headless environment similar to GitHub Actions
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Web scraping imports
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitHubActionsTest:
    """Test class for GitHub Actions environment"""
    
    def __init__(self):
        self.driver = None
        self.test_url = 'https://antiochboone.com/calendar-prayer'
        
    def setup_browser(self) -> bool:
        """Setup Chrome browser with GitHub Actions-like settings"""
        try:
            chrome_options = Options()
            
            # Simulate GitHub Actions headless environment
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Use ChromeDriverManager for local testing
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set timeouts
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            logger.info("✅ Browser setup successful (GitHub Actions simulation)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {str(e)}")
            return False
    
    def test_page_load(self) -> bool:
        """Test if the page loads successfully"""
        try:
            logger.info(f"🌐 Loading page: {self.test_url}")
            self.driver.get(self.test_url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Check page title
            page_title = self.driver.title
            logger.info(f"📄 Page title: {page_title}")
            
            # Check if calendar elements are present
            calendar_elements = self.driver.find_elements(By.CLASS_NAME, "fc-toolbar-title")
            if calendar_elements:
                logger.info(f"✅ Calendar toolbar found: {len(calendar_elements)} elements")
                for elem in calendar_elements:
                    logger.info(f"   - {elem.text}")
            else:
                logger.warning("⚠️ Calendar toolbar not found")
            
            # Check for event elements
            event_elements = self.driver.find_elements(By.CLASS_NAME, "fc-event")
            logger.info(f"📅 Event elements found: {len(event_elements)}")
            
            # Save page source for debugging
            with open('test_page_source.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            logger.info("💾 Page source saved to test_page_source.html")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Page load test failed: {str(e)}")
            return False
    
    def test_calendar_navigation(self) -> bool:
        """Test calendar navigation functionality"""
        try:
            logger.info("🧭 Testing calendar navigation...")
            
            # Find navigation buttons
            prev_button = self.driver.find_elements(By.CLASS_NAME, "fc-prev-button")
            next_button = self.driver.find_elements(By.CLASS_NAME, "fc-next-button")
            
            if prev_button and next_button:
                logger.info("✅ Navigation buttons found")
                
                # Get current month/year
                current_month = self.driver.find_element(By.CLASS_NAME, "fc-toolbar-title").text
                logger.info(f"📅 Current month: {current_month}")
                
                # Try to navigate to next month
                try:
                    next_button[0].click()
                    time.sleep(3)
                    next_month = self.driver.find_element(By.CLASS_NAME, "fc-toolbar-title").text
                    logger.info(f"📅 Next month: {next_month}")
                    
                    # Navigate back
                    prev_button[0].click()
                    time.sleep(3)
                    back_month = self.driver.find_element(By.CLASS_NAME, "fc-toolbar-title").text
                    logger.info(f"📅 Back to: {back_month}")
                    
                    return True
                    
                except Exception as nav_error:
                    logger.error(f"❌ Navigation failed: {nav_error}")
                    return False
            else:
                logger.warning("⚠️ Navigation buttons not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Calendar navigation test failed: {str(e)}")
            return False
    
    def test_event_extraction(self) -> bool:
        """Test event extraction from the calendar"""
        try:
            logger.info("🔍 Testing event extraction...")
            
            # Find all event elements
            events = self.driver.find_elements(By.CLASS_NAME, "fc-event")
            logger.info(f"📅 Found {len(events)} events")
            
            extracted_events = []
            for i, event in enumerate(events[:5]):  # Limit to first 5 events
                try:
                    event_data = {
                        'index': i,
                        'text': event.text,
                        'title': event.get_attribute('title') or 'No title',
                        'class': event.get_attribute('class'),
                        'href': event.get_attribute('href') or 'No href'
                    }
                    extracted_events.append(event_data)
                    logger.info(f"   Event {i+1}: {event_data['title']}")
                    
                except Exception as event_error:
                    logger.error(f"❌ Failed to extract event {i}: {event_error}")
            
            # Save extracted events
            with open('test_extracted_events.json', 'w', encoding='utf-8') as f:
                json.dump(extracted_events, f, indent=2, default=str)
            logger.info("💾 Extracted events saved to test_extracted_events.json")
            
            return len(extracted_events) > 0
            
        except Exception as e:
            logger.error(f"❌ Event extraction test failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting GitHub Actions simulation tests...")
        
        try:
            # Setup browser
            if not self.setup_browser():
                logger.error("❌ Browser setup failed - cannot continue tests")
                return False
            
            # Run tests
            tests = [
                ("Page Load", self.test_page_load),
                ("Calendar Navigation", self.test_calendar_navigation),
                ("Event Extraction", self.test_event_extraction)
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
            logger.info("\n📊 Test Results Summary:")
            passed = sum(results.values())
            total = len(results)
            logger.info(f"Passed: {passed}/{total}")
            
            for test_name, result in results.items():
                status = "✅ PASS" if result else "❌ FAIL"
                logger.info(f"  {status} - {test_name}")
            
            return passed == total
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {str(e)}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("🧹 Browser cleaned up")

if __name__ == "__main__":
    # Check if running in headless mode
    import sys
    if '--headless' in sys.argv:
        os.environ['GITHUB_ACTIONS'] = 'true'
        logger.info("🔧 Running in headless mode (GitHub Actions simulation)")
    
    tester = GitHubActionsTest()
    success = tester.run_all_tests()
    
    if success:
        logger.info("🎉 All tests passed! GitHub Actions should work.")
        sys.exit(0)
    else:
        logger.error("💥 Some tests failed. Check the logs above.")
        sys.exit(1)
