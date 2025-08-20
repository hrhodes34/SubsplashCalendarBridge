#!/usr/bin/env python3
"""
Test Scraper for Subsplash Calendar
This script tests the scraping functionality without requiring Google Calendar credentials
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

# Web scraping imports
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestSubsplashScraper:
    """Test scraper that focuses only on extracting events from Subsplash"""
    
    def __init__(self, calendar_url: str):
        self.calendar_url = calendar_url
        self.driver = None
        
        logger.info(f"Initialized test scraper for: {calendar_url}")
    
    def setup_browser(self) -> bool:
        """Setup Chrome browser for web scraping"""
        try:
            chrome_options = Options()
            
            # For testing, we'll use visible browser to see what's happening
            # chrome_options.add_argument('--headless')
            
            # Additional options for stability
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # Setup Chrome driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("Browser setup successful")
            return True
            
        except Exception as e:
            logger.error(f"Browser setup failed: {str(e)}")
            return False
    
    def scrape_current_page(self) -> List[Dict]:
        """Scrape events from the current calendar page"""
        events = []
        
        try:
            # Wait for calendar content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            logger.info(f"Page loaded successfully. Content length: {len(page_source)} characters")
            
            # Save HTML for inspection
            with open('test_page_source.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            logger.info("Saved page source to test_page_source.html")
            
            # Try multiple selectors to find events
            event_selectors = [
                'div.kit-list-item__text',
                'div.kit-list-item',
                'div[class*="list-item"]',
                'div[class*="event"]',
                'div[class*="calendar"]',
                'article',
                'li',
                'div[data-testid*="event"]',
                'div[class*="subsplash"]',
                'div[class*="kit"]',
                'div[class*="item"]',
                'div[class*="entry"]',
                'div[class*="post"]'
            ]
            
            for selector in event_selectors:
                try:
                    event_elements = soup.select(selector)
                    if event_elements:
                        logger.info(f"Found {len(event_elements)} elements with selector: {selector}")
                        
                        for i, element in enumerate(event_elements[:5]):  # Limit to first 5 for testing
                            event = self._extract_event_from_element(element)
                            if event:
                                events.append(event)
                                logger.info(f"  Event {i+1}: {event['title']}")
                        
                        if events:
                            break  # Found events, no need to try other selectors
                            
                except Exception as e:
                    logger.warning(f"Error with selector {selector}: {str(e)}")
                    continue
            
            # If no events found with selectors, try text analysis
            if not events:
                logger.info("No events found with selectors, trying text analysis...")
                text_events = self._extract_events_from_text(soup)
                if text_events:
                    events.extend(text_events)
                    logger.info(f"Text analysis found {len(text_events)} events")
            
            return events
            
        except Exception as e:
            logger.error(f"Error extracting events from current page: {str(e)}")
            return events
    
    def _extract_event_from_element(self, element) -> Optional[Dict]:
        """Extract event data from a single HTML element"""
        try:
            # Get text content
            text_content = element.get_text(strip=True)
            if not text_content or len(text_content) < 5:
                return None
            
            # Try to extract title (first line that looks like an event title)
            lines = text_content.split('\n')
            title = None
            
            for line in lines:
                line = line.strip()
                if (line and len(line) > 3 and len(line) < 100 and 
                    not self._looks_like_datetime(line) and 
                    line[0].isupper()):
                    title = line
                    break
            
            if not title:
                return None
            
            # Try to extract datetime information
            datetime_info = self._extract_datetime_from_text(text_content)
            if not datetime_info:
                # If no datetime found, create a basic event with today's date
                today = datetime.now()
                start_time = today
                end_time = today + timedelta(hours=1)
            else:
                start_time, end_time = datetime_info
            
            # Create event object
            event = {
                'title': title,
                'start': start_time,
                'end': end_time,
                'description': text_content,
                'location': 'Antioch Boone',
                'all_day': self._is_all_day_event(start_time, end_time),
                'raw_text': text_content  # Include raw text for debugging
            }
            
            return event
            
        except Exception as e:
            logger.warning(f"Error extracting event from element: {str(e)}")
            return None
    
    def _extract_datetime_from_text(self, text: str) -> Optional[Tuple[datetime, datetime]]:
        """Extract datetime information from text"""
        try:
            # Common date patterns
            date_patterns = [
                r'([A-Za-z]+ \d{1,2},? \d{4})',
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{1,2}-\d{1,2}-\d{4})'
            ]
            
            # Time patterns
            time_patterns = [
                r'(\d{1,2}:\d{2}[ap]m)',
                r'(\d{1,2}:\d{2} [ap]m)',
                r'(\d{1,2}:\d{2})'
            ]
            
            # Find dates
            dates = []
            for pattern in date_patterns:
                import re
                matches = re.findall(pattern, text)
                dates.extend(matches)
            
            # Find times
            times = []
            for pattern in time_patterns:
                matches = re.findall(pattern, text)
                times.extend(matches)
            
            if not dates:
                return None
            
            # Parse the first date found
            date_str = dates[0]
            try:
                # Try different date formats
                for fmt in ['%B %d, %Y', '%B %d %Y', '%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y']:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    # If no format worked, try dateutil
                    try:
                        from dateutil import parser
                        parsed_date = parser.parse(date_str)
                    except:
                        return None
            except:
                return None
            
            # Parse time if available
            start_time = parsed_date
            end_time = parsed_date + timedelta(hours=1)  # Default 1 hour duration
            
            if times:
                try:
                    time_str = times[0]
                    # Parse time
                    if 'pm' in time_str.lower():
                        time_str = time_str.replace('pm', '').replace('PM', '').strip()
                        hour = int(time_str.split(':')[0])
                        if hour != 12:
                            hour += 12
                        minute = int(time_str.split(':')[1])
                    elif 'am' in time_str.lower():
                        time_str = time_str.replace('am', '').replace('AM', '').strip()
                        hour = int(time_str.split(':')[0])
                        if hour == 12:
                            hour = 0
                        minute = int(time_str.split(':')[1])
                    else:
                        hour, minute = map(int, time_str.split(':'))
                    
                    start_time = parsed_date.replace(hour=hour, minute=minute)
                    end_time = start_time + timedelta(hours=1)
                except:
                    pass
            
            return start_time, end_time
            
        except Exception as e:
            logger.warning(f"Error extracting datetime from text: {str(e)}")
            return None
    
    def _looks_like_datetime(self, text: str) -> bool:
        """Check if text looks like a datetime string"""
        datetime_indicators = [
            'am', 'pm', 'edt', 'est', 'from', 'to', 'august', 'september', 'october', 
            'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june', 'july'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in datetime_indicators)
    
    def _is_all_day_event(self, start_time: datetime, end_time: datetime) -> bool:
        """Check if event is all-day based on start and end times"""
        if not start_time or not end_time:
            return False
        
        # Check if times are midnight (all-day events typically start/end at midnight)
        return (start_time.hour == 0 and start_time.minute == 0 and 
                end_time.hour == 0 and end_time.minute == 0)
    
    def _extract_events_from_text(self, soup) -> List[Dict]:
        """Fallback method to extract events from page text"""
        events = []
        
        try:
            # Get all text from the page
            all_text = soup.get_text()
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            
            # Look for lines that might be event titles
            for line in lines:
                if (len(line) > 10 and len(line) < 100 and 
                    line[0].isupper() and 
                    not self._looks_like_datetime(line)):
                    
                    # Try to create a basic event
                    event = self._create_event_from_text_line(line)
                    if event:
                        events.append(event)
            
            return events
            
        except Exception as e:
            logger.warning(f"Error extracting events from text: {str(e)}")
            return events
    
    def _create_event_from_text_line(self, text_line: str) -> Optional[Dict]:
        """Create a basic event from a text line"""
        try:
            # This is a fallback method - we'll create a basic event
            # with today's date and the text as title
            today = datetime.now()
            
            event = {
                'title': text_line,
                'start': today,
                'end': today + timedelta(hours=1),
                'description': text_line,
                'location': 'Antioch Boone',
                'all_day': False,
                'raw_text': text_line
            }
            
            return event
            
        except Exception as e:
            logger.warning(f"Error creating event from text line: {str(e)}")
            return None
    
    def run_test_scrape(self) -> List[Dict]:
        """Run a test scrape of the calendar"""
        events = []
        
        try:
            if not self.setup_browser():
                return events
            
            # Navigate to the calendar page
            logger.info(f"Navigating to: {self.calendar_url}")
            self.driver.get(self.calendar_url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Extract events from current page
            current_page_events = self.scrape_current_page()
            if current_page_events:
                events.extend(current_page_events)
                logger.info(f"Found {len(current_page_events)} events on current page")
            else:
                logger.info("No events found on current page")
            
            return events
            
        except Exception as e:
            logger.error(f"Error during test scrape: {str(e)}")
            return events
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Main test function"""
    logger.info("🧪 Starting Subsplash Calendar Test Scrape")
    
    # Test with the Prayer calendar (which should have the events we know about)
    test_url = "https://antiochboone.com/calendar-prayer"
    
    logger.info(f"Testing with URL: {test_url}")
    logger.info("Expected events:")
    logger.info("  - 8/21 6:30 AM Early Morning Prayer")
    logger.info("  - 8/26 5:15 PM Prayer Set") 
    logger.info("  - 8/28 6:30 AM Early Morning Prayer")
    
    # Create scraper and run test
    scraper = TestSubsplashScraper(test_url)
    events = scraper.run_test_scrape()
    
    # Display results
    print("\n" + "="*80)
    print("📊 SCRAPING RESULTS")
    print("="*80)
    
    if events:
        print(f"✅ Successfully found {len(events)} events!")
        print()
        
        for i, event in enumerate(events, 1):
            print(f"Event {i}:")
            print(f"  Title: {event['title']}")
            print(f"  Start: {event['start']}")
            print(f"  End: {event['end']}")
            print(f"  All Day: {event['all_day']}")
            print(f"  Location: {event['location']}")
            print(f"  Raw Text: {event['raw_text'][:100]}...")
            print()
    else:
        print("❌ No events found")
        print("\nThis could mean:")
        print("- The calendar page has no events")
        print("- The selectors need to be updated")
        print("- The page structure is different than expected")
        print("\nCheck the saved HTML file 'test_page_source.html' for manual inspection")
    
    print("="*80)
    print("🔍 Check 'test_page_source.html' for the raw page content")
    print("📝 Review the logs above for detailed extraction information")

if __name__ == "__main__":
    main()
