#!/usr/bin/env python3
"""
Month Navigator Scraper for Subsplash FullCalendar Events
This script navigates through multiple months to find recurring events
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import re

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

class MonthNavigatorScraper:
    """Scraper that navigates through multiple months to find recurring events"""
    
    def __init__(self, calendar_url: str):
        self.calendar_url = calendar_url
        self.driver = None
        self.all_events = []
        
        logger.info(f"Initialized month navigator for: {calendar_url}")
    
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
    
    def get_current_month_year(self) -> Tuple[str, str]:
        """Get the current month and year displayed in the calendar"""
        try:
            # Look for the month/year title in the calendar header
            month_year_element = self.driver.find_element(By.CLASS_NAME, "fc-toolbar-title")
            month_year_text = month_year_element.text.strip()
            
            # Parse "August 2025" format
            parts = month_year_text.split()
            if len(parts) == 2:
                month = parts[0]
                year = parts[1]
                return month, year
            else:
                logger.warning(f"Unexpected month/year format: {month_year_text}")
                return "Unknown", "Unknown"
                
        except Exception as e:
            logger.error(f"Error getting current month/year: {str(e)}")
            return "Unknown", "Unknown"
    
    def navigate_to_next_month(self) -> bool:
        """Click the next month button to navigate forward"""
        try:
            # Find and click the next month button
            next_button = self.driver.find_element(By.CLASS_NAME, "fc-next-button")
            next_button.click()
            
            # Wait for the calendar to update
            time.sleep(3)
            
            # Wait for new events to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "fc-event"))
            )
            
            logger.info("Successfully navigated to next month")
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to next month: {str(e)}")
            return False
    
    def scrape_current_month_events(self) -> List[Dict]:
        """Scrape events from the currently displayed month"""
        events = []
        
        try:
            # Get current month/year
            month, year = self.get_current_month_year()
            logger.info(f"Scraping events for {month} {year}")
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Look specifically for FullCalendar events
            fc_events = soup.find_all('a', class_='fc-event')
            logger.info(f"Found {len(fc_events)} events in {month} {year}")
            
            for i, event_element in enumerate(fc_events):
                try:
                    event = self._extract_fc_event(event_element, month, year)
                    if event:
                        events.append(event)
                        logger.info(f"  Event {i+1}: {event['title']} on {event['start']}")
                except Exception as e:
                    logger.warning(f"Error extracting event {i+1}: {str(e)}")
                    continue
            
            return events
            
        except Exception as e:
            logger.error(f"Error scraping current month events: {str(e)}")
            return events
    
    def _extract_fc_event(self, event_element, month: str, year: str) -> Optional[Dict]:
        """Extract event data from a FullCalendar event element"""
        try:
            # Get the event title
            title_element = event_element.find('div', class_='fc-event-title')
            if not title_element:
                return None
            
            title = title_element.get_text(strip=True)
            if not title:
                return None
            
            # Get the event time
            time_element = event_element.find('div', class_='fc-event-time')
            time_str = time_element.get_text(strip=True) if time_element else ""
            
            # Get the date from the parent day cell
            date_cell = event_element.find_parent('td', attrs={'data-date': True})
            if not date_cell:
                return None
            
            date_str = date_cell.get('data-date')  # Format: "2025-08-21"
            if not date_str:
                return None
            
            # Parse the date
            try:
                event_date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                logger.warning(f"Could not parse date: {date_str}")
                return None
            
            # Parse the time
            start_time, end_time = self._parse_fc_time(time_str, event_date)
            
            # Get event URL if available
            event_url = event_element.get('href', '')
            
            # Create event object
            event = {
                'title': title,
                'start': start_time,
                'end': end_time,
                'date': date_str,
                'time': time_str,
                'month': month,
                'year': year,
                'url': event_url,
                'all_day': self._is_all_day_event(start_time, end_time),
                'raw_html': str(event_element)[:200] + "..."  # Include raw HTML for debugging
            }
            
            return event
            
        except Exception as e:
            logger.warning(f"Error extracting FC event: {str(e)}")
            return None
    
    def _parse_fc_time(self, time_str: str, event_date: datetime) -> Tuple[datetime, datetime]:
        """Parse FullCalendar time format and return start/end times"""
        try:
            if not time_str:
                # No time specified, treat as all-day event
                start_time = event_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(days=1)
                return start_time, end_time
            
            # Parse time formats like "6:30a", "5:15p", "10:00"
            time_str = time_str.lower().strip()
            
            # Handle AM/PM
            if 'a' in time_str:
                time_str = time_str.replace('a', '').strip()
                hour = int(time_str.split(':')[0])
                if hour == 12:
                    hour = 0
                minute = int(time_str.split(':')[1])
            elif 'p' in time_str:
                time_str = time_str.replace('p', '').strip()
                hour = int(time_str.split(':')[0])
                if hour != 12:
                    hour += 12
                minute = int(time_str.split(':')[1])
            else:
                # 24-hour format
                hour, minute = map(int, time_str.split(':'))
            
            # Create start time
            start_time = event_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Default duration: 1 hour
            end_time = start_time + timedelta(hours=1)
            
            return start_time, end_time
            
        except Exception as e:
            logger.warning(f"Error parsing time '{time_str}': {str(e)}")
            # Fallback: create all-day event
            start_time = event_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=1)
            return start_time, end_time
    
    def _is_all_day_event(self, start_time: datetime, end_time: datetime) -> bool:
        """Check if event is all-day based on start and end times"""
        if not start_time or not end_time:
            return False
        
        # Check if times are midnight (all-day events typically start/end at midnight)
        return (start_time.hour == 0 and start_time.minute == 0 and 
                end_time.hour == 0 and end_time.minute == 0)
    
    def run_multi_month_scrape(self, target_months: List[str] = None) -> List[Dict]:
        """Run a multi-month scrape of the FullCalendar"""
        if target_months is None:
            target_months = ["August", "September", "October"]
        
        all_events = []
        
        try:
            if not self.setup_browser():
                return all_events
            
            # Navigate to the calendar page
            logger.info(f"Navigating to: {self.calendar_url}")
            self.driver.get(self.calendar_url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Start with current month
            current_month, current_year = self.get_current_month_year()
            logger.info(f"Starting with current month: {current_month} {current_year}")
            
            # Scrape current month
            current_events = self.scrape_current_month_events()
            all_events.extend(current_events)
            logger.info(f"Collected {len(current_events)} events from {current_month}")
            
            # Navigate through target months
            for target_month in target_months:
                if target_month == current_month:
                    logger.info(f"Already on {target_month}, skipping...")
                    continue
                
                logger.info(f"Navigating to {target_month}...")
                
                # Navigate to next month
                if not self.navigate_to_next_month():
                    logger.error(f"Failed to navigate to {target_month}")
                    break
                
                # Verify we're on the right month
                actual_month, actual_year = self.get_current_month_year()
                if target_month not in actual_month:
                    logger.warning(f"Expected {target_month}, but calendar shows {actual_month}")
                
                # Scrape this month's events
                month_events = self.scrape_current_month_events()
                all_events.extend(month_events)
                logger.info(f"Collected {len(month_events)} events from {actual_month}")
                
                # Small delay between months
                time.sleep(2)
            
            return all_events
            
        except Exception as e:
            logger.error(f"Error during multi-month scrape: {str(e)}")
            return all_events
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Main test function"""
    logger.info("🗓️ Starting Multi-Month FullCalendar Scrape")
    
    # Test with the Prayer calendar
    test_url = "https://antiochboone.com/calendar-prayer"
    
    logger.info(f"Testing with URL: {test_url}")
    logger.info("Expected recurring events:")
    logger.info("  - Prayer Set: Every Tuesday at 5:15 PM")
    logger.info("  - Early Morning Prayer: Every Thursday at 6:30 AM")
    logger.info("Target months: August, September, October")
    
    # Create scraper and run multi-month test
    scraper = MonthNavigatorScraper(test_url)
    all_events = scraper.run_multi_month_scrape()
    
    # Display results
    print("\n" + "="*80)
    print("🗓️ MULTI-MONTH SCRAPING RESULTS")
    print("="*80)
    
    if all_events:
        print(f"✅ Successfully found {len(all_events)} total events across all months!")
        print()
        
        # Group events by month
        events_by_month = {}
        for event in all_events:
            month_key = f"{event['month']} {event['year']}"
            if month_key not in events_by_month:
                events_by_month[month_key] = []
            events_by_month[month_key].append(event)
        
        # Display events grouped by month
        for month_key, month_events in events_by_month.items():
            print(f"📅 {month_key} ({len(month_events)} events):")
            for event in month_events:
                print(f"  • {event['title']} - {event['date']} at {event['time']}")
            print()
        
        # Summary statistics
        print("📊 SUMMARY:")
        print(f"  Total Events: {len(all_events)}")
        print(f"  Months Covered: {len(events_by_month)}")
        
        # Check for expected recurring patterns
        prayer_set_events = [e for e in all_events if "Prayer Set" in e['title']]
        early_prayer_events = [e for e in all_events if "Early Morning Prayer" in e['title']]
        
        print(f"  Prayer Set Events: {len(prayer_set_events)}")
        print(f"  Early Morning Prayer Events: {len(early_prayer_events)}")
        
    else:
        print("❌ No events found across all months")
        print("\nThis could mean:")
        print("- The calendar navigation isn't working")
        print("- The months don't have events")
        print("- The scraping logic needs adjustment")
    
    print("="*80)
    print("🔍 Check the logs above for detailed navigation and extraction information")

if __name__ == "__main__":
    main()
