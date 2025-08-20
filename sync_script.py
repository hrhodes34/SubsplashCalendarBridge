#!/usr/bin/env python3
"""
Subsplash to Google Calendar Sync Script
This script runs automatically via GitHub Actions to sync events from Subsplash to Google Calendar.
"""

import os
import json
import re
import requests
from datetime import datetime, timedelta
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time
from dateutil import parser
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configuration
SCOPES = ['https://www.googleapis.com/auth/calendar']
GOOGLE_CALENDAR_ID = os.environ.get('GOOGLE_CALENDAR_ID')
SUBSPLASH_EMBED_URL = os.environ.get('SUBSPLASH_EMBED_URL')

class SubsplashSyncService:
    def __init__(self):
        self.calendar_service = None
        self.credentials = None
        
    def authenticate_google(self):
        """Authenticate with Google Calendar API using Service Account"""
        try:
            # Load service account credentials from file created by GitHub Actions
            if os.path.exists('credentials.json'):
                # For Service Accounts, we use service_account.Credentials
                self.credentials = service_account.Credentials.from_service_account_file(
                    'credentials.json',
                    scopes=SCOPES
                )
                
                # Build service
                self.calendar_service = build('calendar', 'v3', credentials=self.credentials)
                print("✅ Google Calendar authentication successful")
                return True
            else:
                print("❌ credentials.json not found")
                return False
                
        except Exception as e:
            print(f"❌ Google Calendar authentication failed: {str(e)}")
            return False
    
    def scrape_subsplash_events(self):
        """
        Scrape real events from Subsplash calendar with improved thoroughness
        """
        try:
            print("🔍 Scraping Subsplash events with enhanced discovery...")
            
            # Subsplash embed URL from your calendar
            subsplash_url = "https://subsplash.com/+wrmm/lb/ca/+pysr4r6?embed"
            
            # Try different URL variations to get more events
            url_variations = [
                subsplash_url,
                subsplash_url.replace("?embed", ""),
                subsplash_url.replace("?embed", "?view=calendar"),
                subsplash_url.replace("?embed", "?view=list"),
                subsplash_url.replace("?embed", "?view=month"),
                subsplash_url.replace("?embed", "?view=year"),
                subsplash_url + "&limit=100",
                subsplash_url + "&limit=200",
                subsplash_url + "&limit=500",
                subsplash_url + "&show_all=1",
                subsplash_url + "&include_past=1",
                subsplash_url + "&include_future=1",
                subsplash_url + "&future_events=1",
                subsplash_url + "&all_events=1",
                subsplash_url + "&range=all",
                subsplash_url + "&range=future",
                subsplash_url + "&range=year",
                subsplash_url + "&range=6months",
                subsplash_url + "&range=12months",
                subsplash_url + "&months_ahead=6",
                subsplash_url + "&months_ahead=12",
                subsplash_url + "&months_ahead=24",
                subsplash_url + "&start_date=today",
                subsplash_url + "&end_date=2026-12-31",
                subsplash_url + "&end_date=2027-12-31",
                subsplash_url + "&end_date=2028-12-31",
                subsplash_url + "&timeframe=all",
                subsplash_url + "&timeframe=future",
                subsplash_url + "&timeframe=year",
                subsplash_url + "&timeframe=extended",
                subsplash_url + "&expand=1",
                subsplash_url + "&full=1",
                subsplash_url + "&complete=1",
                subsplash_url + "&all=1",
                # Add more aggressive future loading parameters
                subsplash_url + "&months_ahead=36",
                subsplash_url + "&months_ahead=48",
                subsplash_url + "&months_ahead=60",
                subsplash_url + "&end_date=2030-12-31",
                subsplash_url + "&end_date=2035-12-31",
                subsplash_url + "&range=extended",
                subsplash_url + "&range=unlimited",
                subsplash_url + "&load_all_future=1",
                subsplash_url + "&future_limit=none",
                # Try different calendar navigation approaches
                subsplash_url + "&nav=next_year",
                subsplash_url + "&nav=extended",
                subsplash_url + "&nav=all_future",
                # Try to force full calendar load
                subsplash_url + "&force_load=1",
                subsplash_url + "&preload=1",
                subsplash_url + "&cache=1",
                # Try different event loading strategies
                subsplash_url + "&load_strategy=all",
                subsplash_url + "&load_strategy=future",
                subsplash_url + "&load_strategy=extended",
                # Try to trigger lazy loading
                subsplash_url + "&lazy_load=1",
                subsplash_url + "&infinite_scroll=1",
                subsplash_url + "&auto_load=1"
            ]
            
            all_events = []
            
            for url in url_variations:
                try:
                    print(f"🔍 Trying URL variation: {url}")
                    events = self._scrape_single_url(url)
                    if events:
                        all_events.extend(events)
                        print(f"✅ URL {url}: Found {len(events)} events")
                    else:
                        print(f"❌ URL {url}: No events found")
                except Exception as e:
                    print(f"⚠️ Error with URL {url}: {str(e)}")
                    continue
            
            # Try to find and call potential API endpoints
            print("🔍 Looking for API endpoints...")
            api_events = self._try_api_endpoints(subsplash_url)
            if api_events:
                all_events.extend(api_events)
                print(f"✅ API endpoints: Found {len(api_events)} events")
            
            # Try to simulate user interactions to load more events
            print("🔍 Trying to load more events through user simulation...")
            interaction_events = self._try_user_interactions(subsplash_url)
            if interaction_events:
                all_events.extend(interaction_events)
                print(f"✅ User interactions: Found {len(interaction_events)} events")
            
            # Try to find calendar data in different file formats
            print("🔍 Looking for calendar data in different formats...")
            format_events = self._try_different_formats(subsplash_url)
            if format_events:
                all_events.extend(format_events)
                print(f"✅ Different formats: Found {len(format_events)} events")
            
            # Try to find hidden calendar data in the page
            print("🔍 Looking for hidden calendar data...")
            hidden_events = self._find_hidden_calendar_data(subsplash_url)
            if hidden_events:
                all_events.extend(hidden_events)
                print(f"✅ Hidden data: Found {len(hidden_events)} events")
            
            # Try to simulate browser behavior to trigger dynamic loading
            print("🔍 Trying to simulate browser behavior...")
            browser_events = self._simulate_browser_behavior(subsplash_url)
            if browser_events:
                all_events.extend(browser_events)
                print(f"✅ Browser simulation: Found {len(browser_events)} events")
            
            # Try systematic month-by-month calendar scraping
            print("🔍 Trying systematic month-by-month calendar scraping...")
            calendar_events = self._scrape_calendar_month_by_month()
            if calendar_events:
                all_events.extend(calendar_events)
                print(f"✅ Calendar scraping: Found {len(calendar_events)} events")
            
            # Try browser-based month-by-month navigation (clicks actual arrows!)
            print("🌐 Trying browser-based month-by-month navigation...")
            browser_calendar_events = self._scrape_calendar_with_browser_navigation()
            if browser_calendar_events:
                all_events.extend(browser_calendar_events)
                print(f"✅ Browser navigation: Found {len(browser_calendar_events)} events")
            
            # Try alternative calendar navigation approaches
            print("🔍 Trying alternative calendar navigation approaches...")
            alt_calendar_events = self._try_alternative_calendar_navigation()
            if alt_calendar_events:
                all_events.extend(alt_calendar_events)
                print(f"✅ Alternative navigation: Found {len(alt_calendar_events)} events")
            
            # Remove duplicates based on title and start time
            unique_events = self._deduplicate_events(all_events)
            
            # Analyze the events found
            self._analyze_event_distribution(unique_events)
            
            print(f"✅ Found {len(unique_events)} unique events from all sources")
            return unique_events
            
        except Exception as e:
            print(f"❌ Error scraping Subsplash events: {str(e)}")
            return []
    
    def _scrape_single_url(self, url):
        """Scrape events from a single URL"""
        try:
            # Fetch the page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print(f"📄 Page content length: {len(response.content)} characters")
            
            # Save HTML for debugging (only for the main URL)
            if "embed" in url:
                self._save_html_for_debug(response.content, "subsplash_page.html")
            
            # Analyze page structure for debugging
            self._analyze_page_structure(soup)
            
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
            
            events = []
            found_events = False
            
            for selector in event_selectors:
                try:
                    event_items = soup.select(selector)
                    if event_items:
                        print(f"🔍 Found {len(event_items)} items with selector: {selector}")
                        
                        for item in event_items:
                            event = self._extract_event_from_item(item, selector)
                            if event:
                                events.append(event)
                                found_events = True
                        
                        if found_events:
                            break
                except Exception as e:
                    print(f"⚠️ Error with selector {selector}: {str(e)}")
                    continue
            
            # If no events found with selectors, try a broader approach
            if not found_events:
                print("🔍 No events found with standard selectors, trying broader approach...")
                events = self._fallback_event_extraction(soup)
            
            # Try to handle pagination if we found some events but they seem limited
            if len(events) < 10:  # If we found very few events, try pagination
                print("🔍 Few events found, trying to handle pagination...")
                paginated_events = self._handle_pagination(url, headers)
                if paginated_events:
                    events.extend(paginated_events)
            
            return events
            
        except Exception as e:
            print(f"❌ Error scraping URL {url}: {str(e)}")
            return []
    
    def _save_html_for_debug(self, content, filename):
        """Save HTML content for debugging purposes (only in development mode)"""
        try:
            # Only save debug files if we're in development mode
            if os.environ.get('SAVE_DEBUG_FILES', 'false').lower() == 'true':
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content.decode('utf-8', errors='ignore'))
                print(f"💾 Saved HTML debug file: {filename}")
            else:
                print(f"💾 Debug file saving disabled (set SAVE_DEBUG_FILES=true to enable)")
        except Exception as e:
            print(f"⚠️ Could not save debug HTML: {str(e)}")
    
    def _analyze_page_structure(self, soup):
        """Analyze the page structure to understand how events are organized"""
        try:
            # Only do detailed analysis in development mode
            if os.environ.get('VERBOSE_DEBUG', 'false').lower() == 'true':
                print("🔍 Analyzing page structure...")
                
                # Look for common container patterns
                containers = soup.find_all(['div', 'section', 'article', 'main'], class_=True)
                class_counts = {}
                
                for container in containers:
                    classes = container.get('class', [])
                    for cls in classes:
                        if cls not in class_counts:
                            class_counts[cls] = 0
                        class_counts[cls] += 1
                
                # Show most common classes
                sorted_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
                print("📊 Most common CSS classes:")
                for cls, count in sorted_classes[:20]:
                    print(f"   {cls}: {count} instances")
                
                # Look for text that might contain event information
                all_text = soup.get_text()
                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                
                # Look for lines that might be event titles
                potential_events = []
                for line in lines:
                    if len(line) > 10 and len(line) < 100:
                        # Check if it looks like an event title
                        if not any(word in line.lower() for word in ['am', 'pm', 'edt', 'est', 'from', 'to', 'august', 'september', 'october', 'november', 'december']):
                            if line[0].isupper():  # Starts with capital letter
                                potential_events.append(line)
                
                print(f"🔍 Found {len(potential_events)} potential event titles")
                for i, event in enumerate(potential_events[:10]):  # Show first 10
                    print(f"   {i+1}. {event}")
                
                # Look for date patterns in the text
                import re
                date_patterns = [
                    r'[A-Za-z]+ \d{1,2},? \d{4}',
                    r'[A-Za-z]+ \d{1,2}',
                    r'\d{1,2}:\d{2}[ap]m',
                    r'from \d{1,2}:\d{2}[ap]m',
                    r'to \d{1,2}:\d{2}[ap]m'
                ]
                
                all_dates = []
                for pattern in date_patterns:
                    matches = re.findall(pattern, all_text)
                    all_dates.extend(matches)
                
                print(f"🔍 Found {len(all_dates)} date/time patterns")
                for i, date in enumerate(all_dates[:10]):  # Show first 10
                    print(f"   {i+1}. {date}")
            else:
                print("🔍 Page structure analysis disabled (set VERBOSE_DEBUG=true to enable)")
                
        except Exception as e:
            print(f"⚠️ Error analyzing page structure: {str(e)}")
    
    def _handle_pagination(self, base_url, headers):
        """Handle potential pagination in Subsplash calendar"""
        events = []
        
        try:
            # Try different pagination patterns
            pagination_patterns = [
                f"{base_url}&page=",
                f"{base_url}&offset=",
                f"{base_url}&start=",
                f"{base_url}?page=",
                f"{base_url}?offset=",
                f"{base_url}?start="
            ]
            
            for pattern in pagination_patterns:
                for page in range(1, 6):  # Try up to 5 pages
                    try:
                        page_url = f"{pattern}{page}"
                        print(f"🔍 Trying pagination: {page_url}")
                        
                        response = requests.get(page_url, headers=headers, timeout=30)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.content, 'html.parser')
                            page_events = self._extract_events_from_page(soup)
                            
                            if page_events:
                                events.extend(page_events)
                                print(f"📄 Page {page}: Found {len(page_events)} events")
                            else:
                                print(f"📄 Page {page}: No events found, stopping pagination")
                                break
                        else:
                            print(f"📄 Page {page}: HTTP {response.status_code}")
                            break
                            
                    except Exception as e:
                        print(f"⚠️ Error on page {page}: {str(e)}")
                        break
                        
        except Exception as e:
            print(f"⚠️ Error handling pagination: {str(e)}")
        
        return events
    
    def _extract_events_from_page(self, soup):
        """Extract events from a single page"""
        events = []
        
        # Try the same selectors as the main method
        event_selectors = [
            'div.kit-list-item__text',
            'div.kit-list-item',
            'div[class*="list-item"]',
            'div[class*="event"]',
            'div[class*="calendar"]',
            'article',
            'li',
            'div[data-testid*="event"]',
            'div[class*="subsplash"]'
        ]
        
        for selector in event_selectors:
            try:
                event_items = soup.select(selector)
                if event_items:
                    for item in event_items:
                        event = self._extract_event_from_item(item, selector)
                        if event:
                            events.append(event)
                    break
            except Exception as e:
                continue
        
        return events
    
    def _extract_event_from_item(self, item, selector_used):
        """Extract event data from a single item using multiple strategies"""
        try:
            # Strategy 1: Look for title in various elements
            title = None
            title_selectors = [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                '[class*="title"]', '[class*="name"]', '[class*="heading"]',
                'strong', 'b', 'span[class*="title"]'
            ]
            
            for title_sel in title_selectors:
                title_elem = item.select_one(title_sel)
                if title_elem and title_elem.get_text(strip=True):
                    title = title_elem.get_text(strip=True)
                    break
            
            if not title:
                # Try to get any text that might be a title
                text_elements = item.find_all(text=True, recursive=True)
                for text in text_elements:
                    text = text.strip()
                    if text and len(text) > 5 and len(text) < 100:
                        # Check if it looks like an event title
                        if not any(word in text.lower() for word in ['am', 'pm', 'edt', 'est', 'from', 'to', 'august', 'september']):
                            title = text
                            break
            
            if not title:
                return None
            
            # Strategy 2: Look for date/time information
            date_time_text = None
            date_selectors = [
                '[class*="date"]', '[class*="time"]', '[class*="datetime"]',
                '[class*="subtitle"]', '[class*="meta"]', '[class*="info"]',
                'time', 'span[class*="date"]', 'div[class*="date"]'
            ]
            
            for date_sel in date_selectors:
                date_elem = item.select_one(date_sel)
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    if self._looks_like_datetime(date_text):
                        date_time_text = date_text
                        break
            
            # If no date found in specific elements, search all text
            if not date_time_text:
                all_text = item.get_text()
                # Look for date patterns in the text
                import re
                date_patterns = [
                    r'[A-Za-z]+ \d{1,2},? \d{4}',
                    r'[A-Za-z]+ \d{1,2}',
                    r'\d{1,2}:\d{2}[ap]m',
                    r'from \d{1,2}:\d{2}[ap]m',
                    r'to \d{1,2}:\d{2}[ap]m'
                ]
                
                for pattern in date_patterns:
                    matches = re.findall(pattern, all_text)
                    if matches:
                        # Find the context around the match
                        for match in matches:
                            start_idx = all_text.find(match)
                            if start_idx >= 0:
                                context = all_text[max(0, start_idx-50):start_idx+len(match)+50]
                                if self._looks_like_datetime(context):
                                    date_time_text = context.strip()
                                    break
                        if date_time_text:
                            break
            
            if not date_time_text:
                return None
            
            # Strategy 3: Parse the date/time
            parsed_datetime = self._parse_subsplash_datetime(date_time_text)
            if not parsed_datetime:
                return None
            
            start_time, end_time = parsed_datetime
            
            # Strategy 4: Extract description
            description = ""
            desc_selectors = [
                '[class*="summary"]', '[class*="description"]', '[class*="details"]',
                '[class*="content"]', 'p', 'div[class*="text"]'
            ]
            
            for desc_sel in desc_selectors:
                desc_elem = item.select_one(desc_sel)
                if desc_elem:
                    desc_text = desc_elem.get_text(strip=True)
                    if desc_text and desc_text != title and len(desc_text) > 10:
                        description = desc_text
                        break
            
            # If no description found, try to get surrounding text
            if not description:
                all_text = item.get_text()
                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                for line in lines:
                    if line != title and len(line) > 10 and not self._looks_like_datetime(line):
                        description = line
                        break
            
            # Create event
            event = {
                'title': title,
                'start': start_time,
                'end': end_time,
                'description': description,
                'location': 'Antioch Boone',  # Default location
                'all_day': False
            }
            
            print(f"📅 Found event: {title} on {start_time.strftime('%B %d, %Y')}")
            return event
            
        except Exception as e:
            print(f"⚠️ Error extracting event from item: {str(e)}")
            return None
    
    def _fallback_event_extraction(self, soup):
        """Fallback method to extract events when standard selectors fail"""
        events = []
        print("🔍 Using fallback extraction method...")
        
        # Method 1: Look for JSON data in script tags
        json_events = self._extract_events_from_json(soup)
        if json_events:
            events.extend(json_events)
            print(f"📄 Found {len(json_events)} events from JSON data")
        
        # Method 2: Look for any text that contains date patterns
        text_events = self._extract_events_from_text(soup)
        if text_events:
            events.extend(text_events)
            print(f"📄 Found {len(text_events)} events from text analysis")
        
        # Method 3: Look for events in meta tags or data attributes
        meta_events = self._extract_events_from_meta(soup)
        if meta_events:
            events.extend(meta_events)
            print(f"📄 Found {len(meta_events)} events from meta data")
        
        return events
    
    def _extract_events_from_json(self, soup):
        """Extract events from JSON data in script tags"""
        events = []
        
        try:
            # Look for script tags that might contain event data
            script_tags = soup.find_all('script')
            
            for script in script_tags:
                if script.string:
                    script_content = script.string
                    
                    # Look for JSON patterns that might contain events
                    json_patterns = [
                        r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                        r'window\.events\s*=\s*(\[.*?\]);',
                        r'window\.calendar\s*=\s*({.*?});',
                        r'window\.calendarData\s*=\s*({.*?});',
                        r'window\.eventData\s*=\s*({.*?});',
                        r'window\.subsplashData\s*=\s*({.*?});',
                        r'data\s*:\s*(\[.*?\]),',
                        r'events\s*:\s*(\[.*?\]),',
                        r'calendar\s*:\s*({.*?}),',
                        r'calendarData\s*:\s*({.*?}),',
                        r'eventData\s*:\s*({.*?}),',
                        r'subsplashData\s*:\s*({.*?}),',
                        r'var\s+events\s*=\s*(\[.*?\]);',
                        r'var\s+calendar\s*=\s*({.*?});',
                        r'var\s+calendarData\s*=\s*({.*?});',
                        r'const\s+events\s*=\s*(\[.*?\]);',
                        r'const\s+calendar\s*=\s*({.*?});',
                        r'const\s+calendarData\s*=\s*({.*?});',
                        r'let\s+events\s*=\s*(\[.*?\]);',
                        r'let\s+calendar\s*=\s*({.*?});',
                        r'let\s+calendarData\s*=\s*({.*?});'
                    ]
                    
                    for pattern in json_patterns:
                        matches = re.findall(pattern, script_content, re.DOTALL)
                        for match in matches:
                            try:
                                data = json.loads(match)
                                json_events = self._parse_json_events(data)
                                if json_events:
                                    events.extend(json_events)
                            except json.JSONDecodeError:
                                continue
                    
                    # Also look for calendar data in different formats
                    calendar_patterns = [
                        r'calendarData\s*:\s*({.*?})',
                        r'eventList\s*:\s*(\[.*?\])',
                        r'futureEvents\s*:\s*(\[.*?\])',
                        r'upcomingEvents\s*:\s*(\[.*?\])',
                        r'extendedEvents\s*:\s*(\[.*?\])',
                        r'fullCalendar\s*:\s*({.*?})',
                        r'calendarEvents\s*:\s*(\[.*?\])'
                    ]
                    
                    for pattern in calendar_patterns:
                        matches = re.findall(pattern, script_content, re.DOTALL)
                        for match in matches:
                            try:
                                # Try to clean up the match and parse as JSON
                                cleaned_match = match.strip()
                                if cleaned_match.endswith(','):
                                    cleaned_match = cleaned_match[:-1]
                                
                                data = json.loads(cleaned_match)
                                json_events = self._parse_json_events(data)
                                if json_events:
                                    events.extend(json_events)
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            print(f"⚠️ Error extracting events from JSON: {str(e)}")
        
        return events
    
    def _parse_json_events(self, data):
        """Parse events from JSON data structure"""
        events = []
        
        try:
            # Handle different JSON structures
            if isinstance(data, dict):
                # Look for events in common keys
                event_keys = ['events', 'items', 'data', 'calendar', 'list']
                for key in event_keys:
                    if key in data and isinstance(data[key], list):
                        for item in data[key]:
                            event = self._parse_json_event_item(item)
                            if event:
                                events.append(event)
            
            elif isinstance(data, list):
                # Direct list of events
                for item in data:
                    event = self._parse_json_event_item(item)
                    if event:
                        events.append(event)
                        
        except Exception as e:
            print(f"⚠️ Error parsing JSON events: {str(e)}")
        
        return events
    
    def _parse_json_event_item(self, item):
        """Parse a single event item from JSON"""
        try:
            if not isinstance(item, dict):
                return None
            
            # Look for common event field names
            title = None
            start_time = None
            end_time = None
            description = ""
            
            # Title fields
            title_fields = ['title', 'name', 'summary', 'event_name', 'event_title']
            for field in title_fields:
                if field in item and item[field]:
                    title = str(item[field])
                    break
            
            # Date/time fields
            date_fields = ['start', 'start_date', 'start_time', 'date', 'datetime']
            for field in date_fields:
                if field in item and item[field]:
                    try:
                        start_time = parser.parse(str(item[field]))
                        break
                    except:
                        continue
            
            end_fields = ['end', 'end_date', 'end_time', 'end_datetime']
            for field in end_fields:
                if field in item and item[field]:
                    try:
                        end_time = parser.parse(str(item[field]))
                        break
                    except:
                        continue
            
            # Description fields
            desc_fields = ['description', 'summary', 'details', 'content', 'text']
            for field in desc_fields:
                if field in item and item[field]:
                    description = str(item[field])
                    break
            
            if title and start_time:
                if not end_time:
                    # If no end time, assume 1 hour duration
                    end_time = start_time + timedelta(hours=1)
                
                event = {
                    'title': title,
                    'start': start_time,
                    'end': end_time,
                    'description': description,
                    'location': 'Antioch Boone',
                    'all_day': False
                }
                
                return event
                
        except Exception as e:
            print(f"⚠️ Error parsing JSON event item: {str(e)}")
        
        return None
    
    def _extract_events_from_text(self, soup):
        """Extract events from text analysis"""
        events = []
        
        try:
            all_text = soup.get_text()
            
            # Split text into potential event blocks
            # Look for patterns like "Event Name Date Time Description"
            event_patterns = [
                r'([A-Z][^.!?]*?)([A-Za-z]+ \d{1,2},? \d{4}.*?)(?=[A-Z][^.!?]*?[A-Za-z]+ \d{1,2}|$)',
                r'([A-Z][^.!?]*?)([A-Za-z]+ \d{1,2}.*?)(?=[A-Z][^.!?]*?[A-Za-z]+ \d{1,2}|$)'
            ]
            
            for pattern in event_patterns:
                matches = re.findall(pattern, all_text, re.DOTALL)
                for match in matches:
                    if len(match) >= 2:
                        title = match[0].strip()
                        date_time_text = match[1].strip()
                        
                        if len(title) > 5 and len(title) < 100:
                            parsed_datetime = self._parse_subsplash_datetime(date_time_text)
                            if parsed_datetime:
                                start_time, end_time = parsed_datetime
                                
                                event = {
                                    'title': title,
                                    'start': start_time,
                                    'end': end_time,
                                    'description': date_time_text,
                                    'location': 'Antioch Boone',
                                    'all_day': False
                                }
                                
                                events.append(event)
                                print(f"📅 Fallback found event: {title} on {start_time.strftime('%B %d, %Y')}")
        
        except Exception as e:
            print(f"⚠️ Error extracting events from text: {str(e)}")
        
        return events
    
    def _analyze_event_distribution(self, events):
        """Analyze and display information about the events found"""
        try:
            if not events:
                print("📊 No events to analyze")
                return
            
            print(f"\n📊 Event Analysis:")
            print(f"   Total events: {len(events)}")
            
            # Get date range
            start_dates = [event['start'] for event in events if 'start' in event and event['start']]
            end_dates = [event['end'] for event in events if 'end' in event and event['end']]
            
            if start_dates:
                earliest = min(start_dates)
                latest = max(start_dates)
                
                print(f"   Date range: {earliest.strftime('%B %d, %Y')} to {latest.strftime('%B %d, %Y')}")
                
                # Calculate months ahead
                from datetime import datetime
                now = datetime.now()
                months_ahead = ((latest.year - now.year) * 12) + (latest.month - now.month)
                print(f"   Months ahead: {months_ahead}")
                
                # Group events by month
                monthly_counts = {}
                for event in events:
                    if 'start' in event and event['start']:
                        month_key = event['start'].strftime('%B %Y')
                        monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
                
                print(f"   Events by month:")
                sorted_months = sorted(monthly_counts.items(), key=lambda x: datetime.strptime(x[0], '%B %Y'))
                for month, count in sorted_months:
                    print(f"     {month}: {count} events")
            
            # Show some sample events
            print(f"\n📅 Sample events:")
            sorted_events = sorted(events, key=lambda x: x['start'] if 'start' in x and x['start'] else datetime.min)
            for i, event in enumerate(sorted_events[:5], 1):
                if 'start' in event and event['start']:
                    print(f"   {i}. {event['title']} - {event['start'].strftime('%B %d, %Y')}")
            
            if len(events) > 5:
                print(f"   ... and {len(events) - 5} more events")
                
        except Exception as e:
            print(f"⚠️ Error analyzing event distribution: {str(e)}")
    
    def _extract_events_from_meta(self, soup):
        """Extract events from meta tags and data attributes"""
        events = []
        
        try:
            # Look for meta tags with event information
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name', '')
                content = meta.get('content', '')
                
                if 'event' in name.lower() or 'calendar' in name.lower():
                    if content and len(content) > 10:
                        # Try to parse as event data
                        event = self._parse_meta_event(name, content)
                        if event:
                            events.append(event)
            
            # Look for data attributes that might contain event info
            data_elements = soup.find_all(attrs={'data-event': True})
            for element in data_elements:
                event_data = element.get('data-event')
                if event_data:
                    try:
                        data = json.loads(event_data)
                        event = self._parse_json_event_item(data)
                        if event:
                            events.append(event)
                    except:
                        # Try to parse as text
                        event = self._parse_text_event(event_data)
                        if event:
                            events.append(event)
                            
        except Exception as e:
            print(f"⚠️ Error extracting events from meta: {str(e)}")
        
        return events
    
    def _parse_meta_event(self, name, content):
        """Parse event from meta tag content"""
        try:
            # Look for date patterns in the content
            parsed_datetime = self._parse_subsplash_datetime(content)
            if parsed_datetime:
                start_time, end_time = parsed_datetime
                
                # Try to extract title from the content
                title = content
                if len(title) > 100:
                    title = title[:100] + "..."
                
                event = {
                    'title': title,
                    'start': start_time,
                    'end': end_time,
                    'description': content,
                    'location': 'Antioch Boone',
                    'all_day': False
                }
                
                return event
                
        except Exception as e:
            print(f"⚠️ Error parsing meta event: {str(e)}")
        
        return None
    
    def _parse_text_event(self, text):
        """Parse event from text content"""
        try:
            parsed_datetime = self._parse_subsplash_datetime(text)
            if parsed_datetime:
                start_time, end_time = parsed_datetime
                
                # Try to extract title (first line that's not a date)
                lines = text.split('\n')
                title = "Event"
                for line in lines:
                    line = line.strip()
                    if line and not self._looks_like_datetime(line) and len(line) > 3:
                        title = line
                        break
                
                event = {
                    'title': title,
                    'start': start_time,
                    'end': end_time,
                    'description': text,
                    'location': 'Antioch Boone',
                    'all_day': False
                }
                
                return event
                
        except Exception as e:
            print(f"⚠️ Error parsing text event: {str(e)}")
        
        return None
    
    def _try_api_endpoints(self, base_url):
        """Try to find and call potential API endpoints for events"""
        events = []
        
        try:
            # Extract the base domain and path
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            base_domain = f"{parsed.scheme}://{parsed.netloc}"
            path_parts = parsed.path.strip('/').split('/')
            
            # Common API endpoint patterns for Subsplash
            api_patterns = [
                f"{base_domain}/api/events",
                f"{base_domain}/api/calendar",
                f"{base_domain}/api/v1/events",
                f"{base_domain}/api/v1/calendar",
                f"{base_domain}/events.json",
                f"{base_domain}/calendar.json",
                f"{base_domain}/api/events.json",
                f"{base_domain}/api/calendar.json",
                f"{base_domain}/+wrmm/lb/ca/+pysr4r6/events.json",
                f"{base_domain}/+wrmm/lb/ca/+pysr4r6/calendar.json",
                f"{base_domain}/+wrmm/lb/ca/+pysr4r6/api/events",
                f"{base_domain}/+wrmm/lb/ca/+pysr4r6/api/calendar"
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': base_url
            }
            
            for api_url in api_patterns:
                try:
                    print(f"🔍 Trying API endpoint: {api_url}")
                    response = requests.get(api_url, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            api_events = self._parse_json_events(data)
                            if api_events:
                                events.extend(api_events)
                                print(f"✅ API {api_url}: Found {len(api_events)} events")
                                break  # Found a working API, no need to try others
                        except json.JSONDecodeError:
                            # Not JSON, might be HTML or other format
                            print(f"⚠️ API {api_url}: Response is not JSON")
                            continue
                    else:
                        print(f"⚠️ API {api_url}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"⚠️ Error with API {api_url}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error trying API endpoints: {str(e)}")
        
        return events
    
    def _try_user_interactions(self, base_url):
        """Try to simulate user interactions to load more events"""
        events = []
        
        try:
            # Try different interaction patterns
            interaction_patterns = [
                # Try to load more events
                f"{base_url}&action=load_more",
                f"{base_url}&action=expand",
                f"{base_url}&action=show_all",
                f"{base_url}&action=load_future",
                f"{base_url}&action=load_extended",
                
                # Try different calendar navigation
                f"{base_url}&nav=next_month",
                f"{base_url}&nav=next_quarter",
                f"{base_url}&nav=next_year",
                f"{base_url}&nav=extended",
                
                # Try to trigger lazy loading
                f"{base_url}&lazy_load=1",
                f"{base_url}&infinite_scroll=1",
                f"{base_url}&auto_load=1",
                
                # Try different event loading strategies
                f"{base_url}&load_strategy=all",
                f"{base_url}&load_strategy=future",
                f"{base_url}&load_strategy=extended",
                
                # Try to force full calendar load
                f"{base_url}&force_load=1",
                f"{base_url}&preload=1",
                f"{base_url}&cache=1"
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': base_url,
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            for pattern in interaction_patterns:
                try:
                    print(f"🔍 Trying interaction pattern: {pattern}")
                    response = requests.get(pattern, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        # Parse the response
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Try to extract events from this response
                        interaction_events = self._extract_events_from_page(soup)
                        
                        if interaction_events:
                            events.extend(interaction_events)
                            print(f"✅ Interaction {pattern}: Found {len(interaction_events)} events")
                            
                            # If we found events, try to get even more
                            if len(interaction_events) > 0:
                                # Try to go even further into the future
                                extended_events = self._try_extended_future_loading(pattern, headers)
                                if extended_events:
                                    events.extend(extended_events)
                                    print(f"✅ Extended loading: Found {len(extended_events)} more events")
                        else:
                            print(f"⚠️ Interaction {pattern}: No events found")
                    else:
                        print(f"⚠️ Interaction {pattern}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"⚠️ Error with interaction {pattern}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error trying user interactions: {str(e)}")
        
        return events
    
    def _try_extended_future_loading(self, base_url, headers):
        """Try to load events even further into the future"""
        events = []
        
        try:
            # Try to go even further into the future
            extended_patterns = [
                f"{base_url}&months_ahead=36",
                f"{base_url}&months_ahead=48",
                f"{base_url}&months_ahead=60",
                f"{base_url}&end_date=2030-12-31",
                f"{base_url}&end_date=2035-12-31",
                f"{base_url}&range=extended",
                f"{base_url}&range=unlimited",
                f"{base_url}&load_all_future=1",
                f"{base_url}&future_limit=none"
            ]
            
            for pattern in extended_patterns:
                try:
                    print(f"🔍 Trying extended future loading: {pattern}")
                    response = requests.get(pattern, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        extended_events = self._extract_events_from_page(soup)
                        
                        if extended_events:
                            events.extend(extended_events)
                            print(f"✅ Extended {pattern}: Found {len(extended_events)} events")
                        else:
                            print(f"⚠️ Extended {pattern}: No additional events")
                    else:
                        print(f"⚠️ Extended {pattern}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"⚠️ Error with extended loading {pattern}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error with extended future loading: {str(e)}")
        
        return events
    
    def _try_different_formats(self, base_url):
        """Try to find calendar data in different file formats and sources"""
        events = []
        
        try:
            # Try different file extensions and formats
            format_patterns = [
                # JSON formats
                f"{base_url.replace('?embed', '')}.json",
                f"{base_url.replace('?embed', '')}/events.json",
                f"{base_url.replace('?embed', '')}/calendar.json",
                f"{base_url.replace('?embed', '')}/data.json",
                f"{base_url.replace('?embed', '')}/feed.json",
                
                # XML formats
                f"{base_url.replace('?embed', '')}.xml",
                f"{base_url.replace('?embed', '')}/events.xml",
                f"{base_url.replace('?embed', '')}/calendar.xml",
                f"{base_url.replace('?embed', '')}/feed.xml",
                
                # RSS feeds
                f"{base_url.replace('?embed', '')}/rss",
                f"{base_url.replace('?embed', '')}/feed",
                f"{base_url.replace('?embed', '')}/rss.xml",
                f"{base_url.replace('?embed', '')}/feed.xml",
                
                # ICS calendar format
                f"{base_url.replace('?embed', '')}.ics",
                f"{base_url.replace('?embed', '')}/calendar.ics",
                f"{base_url.replace('?embed', '')}/events.ics",
                
                # CSV format
                f"{base_url.replace('?embed', '')}.csv",
                f"{base_url.replace('?embed', '')}/events.csv",
                f"{base_url.replace('?embed', '')}/calendar.csv"
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, application/xml, text/calendar, text/csv, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': base_url
            }
            
            for format_url in format_patterns:
                try:
                    print(f"🔍 Trying format: {format_url}")
                    response = requests.get(format_url, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        
                        if 'json' in content_type:
                            # Parse JSON
                            try:
                                data = response.json()
                                json_events = self._parse_json_events(data)
                                if json_events:
                                    events.extend(json_events)
                                    print(f"✅ JSON format {format_url}: Found {len(json_events)} events")
                            except json.JSONDecodeError:
                                print(f"⚠️ JSON format {format_url}: Invalid JSON")
                                
                        elif 'xml' in content_type or format_url.endswith('.xml'):
                            # Parse XML
                            try:
                                xml_events = self._parse_xml_events(response.content)
                                if xml_events:
                                    events.extend(xml_events)
                                    print(f"✅ XML format {format_url}: Found {len(xml_events)} events")
                            except Exception as e:
                                print(f"⚠️ XML format {format_url}: Error parsing - {str(e)}")
                                
                        elif 'calendar' in content_type or format_url.endswith('.ics'):
                            # Parse ICS calendar
                            try:
                                ics_events = self._parse_ics_events(response.content)
                                if ics_events:
                                    events.extend(ics_events)
                                    print(f"✅ ICS format {format_url}: Found {len(ics_events)} events")
                            except Exception as e:
                                print(f"⚠️ ICS format {format_url}: Error parsing - {str(e)}")
                                
                        elif 'csv' in content_type or format_url.endswith('.csv'):
                            # Parse CSV
                            try:
                                csv_events = self._parse_csv_events(response.content)
                                if csv_events:
                                    events.extend(csv_events)
                                    print(f"✅ CSV format {format_url}: Found {len(csv_events)} events")
                            except Exception as e:
                                print(f"⚠️ CSV format {format_url}: Error parsing - {str(e)}")
                                
                        else:
                            # Try to parse as text and look for event patterns
                            try:
                                text_events = self._parse_text_events(response.content)
                                if text_events:
                                    events.extend(text_events)
                                    print(f"✅ Text format {format_url}: Found {len(text_events)} events")
                            except Exception as e:
                                print(f"⚠️ Text format {format_url}: Error parsing - {str(e)}")
                    else:
                        print(f"⚠️ Format {format_url}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"⚠️ Error with format {format_url}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error trying different formats: {str(e)}")
        
        return events
    
    def _parse_xml_events(self, content):
        """Parse events from XML content"""
        events = []
        
        try:
            soup = BeautifulSoup(content, 'xml')
            
            # Look for common XML event patterns
            event_tags = soup.find_all(['event', 'item', 'entry', 'calendar-event'])
            
            for tag in event_tags:
                try:
                    # Extract event data from XML tags
                    title = tag.find(['title', 'name', 'summary'])
                    title = title.get_text() if title else "Event"
                    
                    # Look for date/time information
                    start_date = tag.find(['start', 'start_date', 'date', 'datetime'])
                    end_date = tag.find(['end', 'end_date', 'end_datetime'])
                    
                    if start_date:
                        start_text = start_date.get_text()
                        parsed_datetime = self._parse_subsplash_datetime(start_text)
                        
                        if parsed_datetime:
                            start_time, end_time = parsed_datetime
                            
                            # Get description
                            description = ""
                            desc_tag = tag.find(['description', 'summary', 'content'])
                            if desc_tag:
                                description = desc_tag.get_text()
                            
                            event = {
                                'title': title,
                                'start': start_time,
                                'end': end_time,
                                'description': description,
                                'location': 'Antioch Boone',
                                'all_day': False
                            }
                            
                            events.append(event)
                            
                except Exception as e:
                    print(f"⚠️ Error parsing XML event: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error parsing XML content: {str(e)}")
        
        return events
    
    def _parse_ics_events(self, content):
        """Parse events from ICS calendar content"""
        events = []
        
        try:
            content_str = content.decode('utf-8', errors='ignore')
            lines = content_str.split('\n')
            
            current_event = {}
            in_event = False
            
            for line in lines:
                line = line.strip()
                
                if line == 'BEGIN:VEVENT':
                    in_event = True
                    current_event = {}
                elif line == 'END:VEVENT':
                    in_event = False
                    if current_event.get('title') and current_event.get('start'):
                        events.append(current_event)
                elif in_event and ':' in line:
                    key, value = line.split(':', 1)
                    
                    if key == 'SUMMARY':
                        current_event['title'] = value
                    elif key == 'DTSTART':
                        # Parse ICS date format
                        try:
                            from dateutil import parser
                            start_time = parser.parse(value)
                            current_event['start'] = start_time
                        except:
                            pass
                    elif key == 'DTEND':
                        try:
                            from dateutil import parser
                            end_time = parser.parse(value)
                            current_event['end'] = end_time
                        except:
                            pass
                    elif key == 'DESCRIPTION':
                        current_event['description'] = value
                        
        except Exception as e:
            print(f"⚠️ Error parsing ICS content: {str(e)}")
        
        return events
    
    def _parse_csv_events(self, content):
        """Parse events from CSV content"""
        events = []
        
        try:
            import csv
            from io import StringIO
            
            content_str = content.decode('utf-8', errors='ignore')
            csv_file = StringIO(content_str)
            reader = csv.DictReader(csv_file)
            
            for row in reader:
                try:
                    # Look for common CSV column names
                    title = row.get('title') or row.get('name') or row.get('summary') or row.get('event')
                    start_date = row.get('start') or row.get('start_date') or row.get('date') or row.get('datetime')
                    
                    if title and start_date:
                        parsed_datetime = self._parse_subsplash_datetime(start_date)
                        
                        if parsed_datetime:
                            start_time, end_time = parsed_datetime
                            
                            description = row.get('description') or row.get('summary') or row.get('details') or ""
                            
                            event = {
                                'title': title,
                                'start': start_time,
                                'end': end_time,
                                'description': description,
                                'location': 'Antioch Boone',
                                'all_day': False
                            }
                            
                            events.append(event)
                            
                except Exception as e:
                    print(f"⚠️ Error parsing CSV row: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error parsing CSV content: {str(e)}")
        
        return events
    
    def _parse_text_events(self, content):
        """Parse events from plain text content"""
        events = []
        
        try:
            content_str = content.decode('utf-8', errors='ignore')
            
            # Look for event patterns in the text
            event_patterns = [
                r'([A-Z][^.!?]*?)([A-Za-z]+ \d{1,2},? \d{4}.*?)(?=[A-Z][^.!?]*?[A-Za-z]+ \d{1,2}|$)',
                r'([A-Z][^.!?]*?)([A-Za-z]+ \d{1,2}.*?)(?=[A-Z][^.!?]*?[A-Za-z]+ \d{1,2}|$)'
            ]
            
            for pattern in event_patterns:
                matches = re.findall(pattern, content_str, re.DOTALL)
                for match in matches:
                    if len(match) >= 2:
                        title = match[0].strip()
                        date_time_text = match[1].strip()
                        
                        if len(title) > 5 and len(title) < 100:
                            parsed_datetime = self._parse_subsplash_datetime(date_time_text)
                            if parsed_datetime:
                                start_time, end_time = parsed_datetime
                                
                                event = {
                                    'title': title,
                                    'start': start_time,
                                    'end': end_time,
                                    'description': date_time_text,
                                    'location': 'Antioch Boone',
                                    'all_day': False
                                }
                                
                                events.append(event)
                                
        except Exception as e:
            print(f"⚠️ Error parsing text content: {str(e)}")
        
        return events
    
    def _looks_like_datetime(self, text):
        """Check if text looks like it contains date/time information"""
        text_lower = text.lower()
        date_indicators = ['am', 'pm', 'edt', 'est', 'from', 'to', 'august', 'september', 'october', 'november', 'december']
        time_indicators = [':', '00', '30', '15', '45']
        
        has_date_word = any(indicator in text_lower for indicator in date_indicators)
        has_time_format = any(indicator in text for indicator in time_indicators)
        
        return has_date_word or has_time_format
    
    def _deduplicate_events(self, events):
        """Remove duplicate events based on title and start time"""
        unique_events = []
        seen_keys = set()
        
        for event in events:
            if not event or 'title' not in event or 'start' not in event:
                continue
                
            # Create a unique key for the event
            start_str = event['start'].strftime('%Y%m%d_%H%M') if hasattr(event['start'], 'strftime') else str(event['start'])
            event_key = f"{event['title']}_{start_str}"
            
            if event_key not in seen_keys:
                seen_keys.add(event_key)
                unique_events.append(event)
        
        return unique_events
    
    def _parse_subsplash_datetime(self, date_time_text):
        """
        Parse Subsplash date/time formats with enhanced pattern recognition:
        - "August 20, 2025 from 6:00 - 8:00pm EDT" (single day)
        - "August 22, 6:00pm - August 24, 2025 11:00am EDT" (multi-day)
        - "August 22, 6:00pm - August 24, 2025 11:00am EDT" (multi-day without year in start)
        - "August 20, 2025 from 6:30 - 7:15am EDT" (single day with different format)
        Returns (start_datetime, end_datetime) or None if parsing fails
        """
        try:
            import re
            from dateutil import parser
            
            # Clean up the text
            date_time_text = date_time_text.strip()
            print(f"🔍 Parsing datetime: {date_time_text}")
            
            # Try single-day format: "August 20, 2025 from 6:00 - 8:00pm EDT"
            single_day_pattern = r'([A-Za-z]+ \d{1,2},? \d{4}) from (\d{1,2}:\d{2})([ap]m) - (\d{1,2}:\d{2})([ap]m)'
            single_match = re.search(single_day_pattern, date_time_text)
            
            if single_match:
                date_str = single_match.group(1)  # "August 20, 2025"
                start_time_str = single_match.group(2)  # "6:00"
                start_ampm = single_match.group(3)  # "pm"
                end_time_str = single_match.group(4)   # "8:00"
                end_ampm = single_match.group(5)       # "pm"
                
                # Parse the date
                date_obj = parser.parse(date_str)
                
                # Parse start time
                start_hour, start_minute = map(int, start_time_str.split(':'))
                if start_ampm.lower() == 'pm' and start_hour != 12:
                    start_hour += 12
                elif start_ampm.lower() == 'am' and start_hour == 12:
                    start_hour = 0
                
                start_datetime = date_obj.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
                
                # Parse end time
                end_hour, end_minute = map(int, end_time_str.split(':'))
                if end_ampm.lower() == 'pm' and end_hour != 12:
                    end_hour += 12
                elif end_ampm.lower() == 'am' and end_hour == 12:
                    end_hour = 0
                
                end_datetime = date_obj.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
                
                return start_datetime, end_datetime
            
            # Try multi-day format: "August 22, 6:00pm - August 24, 2025 11:00am EDT"
            multi_day_pattern = r'([A-Za-z]+ \d{1,2}),? (\d{1,2}:\d{2})([ap]m) - ([A-Za-z]+ \d{1,2},? \d{4}) (\d{1,2}:\d{2})([ap]m)'
            multi_match = re.search(multi_day_pattern, date_time_text)
            
            if multi_match:
                start_date_str = multi_match.group(1)  # "August 22"
                start_time_str = multi_match.group(2)  # "6:00"
                start_ampm = multi_match.group(3)      # "pm"
                end_date_str = multi_match.group(4)    # "August 24, 2025"
                end_time_str = multi_match.group(5)    # "11:00"
                end_ampm = multi_match.group(6)        # "am"
                
                # Parse start date and time
                start_date_obj = parser.parse(start_date_str + ", 2025")  # Assume current year
                start_hour, start_minute = map(int, start_time_str.split(':'))
                if start_ampm.lower() == 'pm' and start_hour != 12:
                    start_hour += 12
                elif start_ampm.lower() == 'am' and start_hour == 12:
                    start_hour = 0
                
                start_datetime = start_date_obj.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
                
                # Parse end date and time
                end_date_obj = parser.parse(end_date_str)
                end_hour, end_minute = map(int, end_time_str.split(':'))
                if end_ampm.lower() == 'pm' and end_hour != 12:
                    end_hour += 12
                elif end_ampm.lower() == 'am' and end_hour == 12:
                    end_hour = 0
                
                end_datetime = end_date_obj.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
                
                return start_datetime, end_datetime
            
            # Try alternative single-day format: "August 20, 2025 from 6:30 - 7:15am EDT"
            alt_single_pattern = r'([A-Za-z]+ \d{1,2},? \d{4}) from (\d{1,2}:\d{2})([ap]m) - (\d{1,2}:\d{2})([ap]m)'
            alt_single_match = re.search(alt_single_pattern, date_time_text)
            
            if alt_single_match:
                date_str = alt_single_match.group(1)  # "August 20, 2025"
                start_time_str = alt_single_match.group(2)  # "6:30"
                start_ampm = alt_single_match.group(3)  # "am"
                end_time_str = alt_single_match.group(4)   # "7:15"
                end_ampm = alt_single_match.group(5)       # "am"
                
                # Parse the date
                date_obj = parser.parse(date_str)
                
                # Parse start time
                start_hour, start_minute = map(int, start_time_str.split(':'))
                if start_ampm.lower() == 'pm' and start_hour != 12:
                    start_hour += 12
                elif start_ampm.lower() == 'am' and start_hour == 12:
                    start_hour = 0
                
                start_datetime = date_obj.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
                
                # Parse end time
                end_hour, end_minute = map(int, end_time_str.split(':'))
                if end_ampm.lower() == 'pm' and end_hour != 12:
                    end_hour += 12
                elif end_ampm.lower() == 'am' and end_hour == 12:
                    end_hour = 0
                
                end_datetime = date_obj.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
                
                return start_datetime, end_datetime
            
            # Try simple date format: "August 20, 2025" (all day event)
            simple_date_pattern = r'([A-Za-z]+ \d{1,2},? \d{4})'
            simple_date_match = re.search(simple_date_pattern, date_time_text)
            
            if simple_date_match:
                date_str = simple_date_match.group(1)  # "August 20, 2025"
                date_obj = parser.parse(date_str)
                
                # Create all-day event
                start_datetime = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
                end_datetime = date_obj.replace(hour=23, minute=59, second=59, microsecond=0)
                
                return start_datetime, end_datetime
            
            # Try to extract any date and time patterns
            date_pattern = r'([A-Za-z]+ \d{1,2},? \d{4})'
            time_pattern = r'(\d{1,2}:\d{2})([ap]m)'
            
            date_match = re.search(date_pattern, date_time_text)
            time_matches = re.findall(time_pattern, date_time_text)
            
            if date_match and len(time_matches) >= 2:
                date_str = date_match.group(1)
                date_obj = parser.parse(date_str)
                
                # Parse first time as start
                start_time_str, start_ampm = time_matches[0]
                start_hour, start_minute = map(int, start_time_str.split(':'))
                if start_ampm.lower() == 'pm' and start_hour != 12:
                    start_hour += 12
                elif start_ampm.lower() == 'am' and start_hour == 12:
                    start_hour = 0
                
                start_datetime = date_obj.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
                
                # Parse second time as end
                end_time_str, end_ampm = time_matches[1]
                end_hour, end_minute = map(int, end_time_str.split(':'))
                if end_ampm.lower() == 'pm' and end_hour != 12:
                    end_hour += 12
                elif end_ampm.lower() == 'am' and end_hour == 12:
                    end_hour = 0
                
                end_datetime = date_obj.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
                
                return start_datetime, end_datetime
            
            print(f"⚠️ Could not parse date/time: {date_time_text}")
            return None
            
        except Exception as e:
            print(f"⚠️ Error parsing datetime '{date_time_text}': {str(e)}")
            return None

    def get_existing_google_events(self, start_date, end_date):
        """Get existing events from Google Calendar"""
        try:
            events_result = self.calendar_service.events().list(
                calendarId=GOOGLE_CALENDAR_ID,
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            print(f"📅 Found {len(events)} existing events in Google Calendar")
            return events
            
        except Exception as e:
            print(f"❌ Error getting existing Google Calendar events: {str(e)}")
            return []
    
    def sync_to_google_calendar(self, subsplash_events):
        """Sync Subsplash events to Google Calendar"""
        try:
            if not self.calendar_service:
                print("❌ Google Calendar service not initialized")
                return False
            
            # Get date range for existing events
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now() + timedelta(days=365)
            
            existing_events = self.get_existing_google_events(start_date, end_date)
            
            # Create a map of existing events by title and start time
            existing_event_map = {}
            for event in existing_events:
                if 'start' in event and 'dateTime' in event['start']:
                    start_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                    key = f"{event['summary']}_{start_time.strftime('%Y%m%d_%H%M')}"
                    existing_event_map[key] = event
            
            synced_count = 0
            updated_count = 0
            
            for event_data in subsplash_events:
                # Create event key for comparison
                event_key = f"{event_data['title']}_{event_data['start'].strftime('%Y%m%d_%H%M')}"
                
                # Prepare event for Google Calendar
                google_event = {
                    'summary': event_data['title'],
                    'description': event_data.get('description', ''),
                    'location': event_data.get('location', ''),
                    'start': {
                        'dateTime': event_data['start'].isoformat(),
                        'timeZone': 'America/New_York'
                    },
                    'end': {
                        'dateTime': event_data['end'].isoformat(),
                        'timeZone': 'America/New_York'
                    }
                }
                
                if event_data.get('all_day', False):
                    google_event['start'] = {'date': event_data['start'].date().isoformat()}
                    google_event['end'] = {'date': event_data['end'].date().isoformat()}
                
                # Check if event already exists
                if event_key in existing_event_map:
                    # Update existing event
                    existing_event = existing_event_map[event_key]
                    try:
                        self.calendar_service.events().update(
                            calendarId=GOOGLE_CALENDAR_ID,
                            eventId=existing_event['id'],
                            body=google_event
                        ).execute()
                        updated_count += 1
                        print(f"🔄 Updated event: {event_data['title']}")
                    except Exception as e:
                        print(f"❌ Error updating event {event_data['title']}: {str(e)}")
                else:
                    # Create new event
                    try:
                        self.calendar_service.events().insert(
                            calendarId=GOOGLE_CALENDAR_ID,
                            body=google_event
                        ).execute()
                        synced_count += 1
                        print(f"✅ Created event: {event_data['title']}")
                    except Exception as e:
                        print(f"❌ Error creating event {event_data['title']}: {str(e)}")
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
            
            print(f"🎯 Sync complete: {synced_count} new events, {updated_count} updated events")
            return True
            
        except Exception as e:
            print(f"❌ Error syncing to Google Calendar: {str(e)}")
            return False
    
    def save_status(self, success, message):
        """Save sync status for GitHub Actions to commit (optional)"""
        try:
            # Only save status file if explicitly enabled
            if os.environ.get('SAVE_STATUS_FILE', 'false').lower() == 'true':
                status = {
                    'last_sync': datetime.now().isoformat(),
                    'success': success,
                    'message': message,
                    'calendar_id': GOOGLE_CALENDAR_ID,
                    'subsplash_url': SUBSPLASH_EMBED_URL
                }
                
                with open('sync_status.json', 'w') as f:
                    json.dump(status, f, indent=2)
                
                print(f"📝 Status saved: {message}")
            else:
                print(f"📝 Status file saving disabled (set SAVE_STATUS_FILE=true to enable)")
                print(f"📝 Sync result: {message}")
                
        except Exception as e:
            print(f"⚠️ Could not save status file: {str(e)}")
            print(f"📝 Sync result: {message}")
    
    def run_sync(self):
        """Main sync method"""
        print("�� Starting Subsplash to Google Calendar sync...")
        print(f"�� Target Calendar ID: {GOOGLE_CALENDAR_ID}")
        print(f"🔗 Subsplash URL: {SUBSPLASH_EMBED_URL}")
        
        # Authenticate with Google
        if not self.authenticate_google():
            self.save_status(False, "Google authentication failed")
            return False
        
        # Scrape Subsplash events
        subsplash_events = self.scrape_subsplash_events()
        if not subsplash_events:
            self.save_status(False, "No events found from Subsplash")
            return False
        
        # Sync to Google Calendar
        if self.sync_to_google_calendar(subsplash_events):
            self.save_status(True, f"Successfully synced {len(subsplash_events)} events")
            return True
        else:
            self.save_status(False, "Sync to Google Calendar failed")
            return False
    
    def _find_hidden_calendar_data(self, base_url):
        """Try to find hidden calendar data in the page that might contain future events"""
        events = []
        
        try:
            # Get the main page to look for hidden data
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(base_url, headers=headers, timeout=60)
            if response.status_code != 200:
                return events
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for hidden input fields that might contain calendar data
            hidden_inputs = soup.find_all('input', type='hidden')
            for hidden_input in hidden_inputs:
                name = hidden_input.get('name', '')
                value = hidden_input.get('value', '')
                
                if any(keyword in name.lower() for keyword in ['calendar', 'event', 'data', 'json']):
                    print(f"🔍 Found hidden input: {name}")
                    try:
                        # Try to parse as JSON
                        if value.startswith('{') or value.startswith('['):
                            data = json.loads(value)
                            hidden_events = self._parse_json_events(data)
                            if hidden_events:
                                events.extend(hidden_events)
                                print(f"✅ Hidden input {name}: Found {len(hidden_events)} events")
                    except:
                        # Try to parse as text
                        if len(value) > 50:
                            text_events = self._parse_text_events(value.encode())
                            if text_events:
                                events.extend(text_events)
                                print(f"✅ Hidden input {name}: Found {len(text_events)} events from text")
            
            # Look for data attributes that might contain event information
            data_elements = soup.find_all(attrs={'data-': True})
            for element in data_elements:
                for attr_name, attr_value in element.attrs.items():
                    if attr_name.startswith('data-') and len(attr_value) > 20:
                        attr_name_lower = attr_name.lower()
                        if any(keyword in attr_name_lower for keyword in ['calendar', 'event', 'data', 'json']):
                            print(f"🔍 Found data attribute: {attr_name}")
                            try:
                                # Try to parse as JSON
                                if attr_value.startswith('{') or attr_value.startswith('['):
                                    data = json.loads(attr_value)
                                    hidden_events = self._parse_json_events(data)
                                    if hidden_events:
                                        events.extend(hidden_events)
                                        print(f"✅ Data attribute {attr_name}: Found {len(hidden_events)} events")
                            except:
                                # Try to parse as text
                                text_events = self._parse_text_events(attr_value.encode())
                                if text_events:
                                    events.extend(text_events)
                                    print(f"✅ Data attribute {attr_name}: Found {len(text_events)} events from text")
            
            # Look for script tags with calendar data
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string:
                    script_content = script.string
                    
                    # Look for more specific calendar data patterns
                    calendar_patterns = [
                        r'calendarData\s*=\s*({.*?});',
                        r'eventList\s*=\s*(\[.*?\]);',
                        r'futureEvents\s*=\s*(\[.*?\]);',
                        r'upcomingEvents\s*=\s*(\[.*?\]);',
                        r'extendedEvents\s*=\s*(\[.*?\]);',
                        r'fullCalendar\s*=\s*({.*?});',
                        r'calendarEvents\s*=\s*(\[.*?\]);',
                        r'eventsData\s*=\s*({.*?});',
                        r'calendarConfig\s*=\s*({.*?});',
                        r'eventConfig\s*=\s*({.*?});',
                        r'subsplashEvents\s*=\s*(\[.*?\]);',
                        r'churchEvents\s*=\s*(\[.*?\]);',
                        r'wrmmEvents\s*=\s*(\[.*?\]);'
                    ]
                    
                    for pattern in calendar_patterns:
                        matches = re.findall(pattern, script_content, re.DOTALL)
                        for match in matches:
                            try:
                                # Clean up the match
                                cleaned_match = match.strip()
                                if cleaned_match.endswith(','):
                                    cleaned_match = cleaned_match[:-1]
                                
                                data = json.loads(cleaned_match)
                                hidden_events = self._parse_json_events(data)
                                if hidden_events:
                                    events.extend(hidden_events)
                                    print(f"✅ Script pattern: Found {len(hidden_events)} events")
                            except:
                                continue
            
            # Look for iframe sources that might contain calendar data
            iframes = soup.find_all('iframe')
            for iframe in iframes:
                src = iframe.get('src', '')
                if src and ('calendar' in src.lower() or 'event' in src.lower()):
                    print(f"🔍 Found calendar iframe: {src}")
                    try:
                        iframe_response = requests.get(src, headers=headers, timeout=30)
                        if iframe_response.status_code == 200:
                            iframe_soup = BeautifulSoup(iframe_response.content, 'html.parser')
                            iframe_events = self._extract_events_from_page(iframe_soup)
                            if iframe_events:
                                events.extend(iframe_events)
                                print(f"✅ Iframe {src}: Found {len(iframe_events)} events")
                    except Exception as e:
                        print(f"⚠️ Error with iframe {src}: {str(e)}")
                        continue
            
        except Exception as e:
            print(f"⚠️ Error finding hidden calendar data: {str(e)}")
        
        return events
    
    def _scrape_calendar_month_by_month(self):
        """Systematically scrape the church's calendar month by month until we find an empty month"""
        events = []
        
        try:
            # Base calendar URL
            base_calendar_url = "https://antiochboone.com/calendar"
            
            # Headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Start from current month and go forward until we find an empty month
            current_date = datetime.now()
            consecutive_empty_months = 0
            max_consecutive_empty = 3  # Stop after 3 consecutive empty months
            max_months_to_check = 60  # Safety limit to prevent infinite loops
            
            print(f"🗓️ Starting systematic calendar scraping from {current_date.strftime('%B %Y')}")
            
            for month_offset in range(max_months_to_check):
                # Calculate the target month
                target_date = current_date + relativedelta(months=month_offset)
                target_month = target_date.month
                target_year = target_date.year
                
                # Try different URL patterns for the month
                month_urls = [
                    f"{base_calendar_url}?month={target_month}&year={target_year}",
                    f"{base_calendar_url}?m={target_month}&y={target_year}",
                    f"{base_calendar_url}/{target_year}/{target_month:02d}",
                    f"{base_calendar_url}/month/{target_year}/{target_month:02d}",
                    f"{base_calendar_url}/calendar/{target_year}/{target_month:02d}",
                    f"{base_calendar_url}?date={target_year}-{target_month:02d}",
                    f"{base_calendar_url}?view=month&month={target_month}&year={target_year}",
                ]
                
                month_events = []
                month_has_events = False
                
                print(f"🔍 Checking {target_date.strftime('%B %Y')}...")
                
                for url in month_urls:
                    try:
                        response = requests.get(url, headers=headers, timeout=30)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.content, 'html.parser')
                            
                            # Try to extract events from this month's page
                            month_page_events = self._extract_events_from_month_page(soup, target_date)
                            
                            if month_page_events:
                                month_events.extend(month_page_events)
                                month_has_events = True
                                print(f"  ✅ Found {len(month_page_events)} events via {url.split('?')[0]}")
                                break  # Found events, no need to try other URL patterns
                            else:
                                print(f"  ⚠️ No events found via {url.split('?')[0]}")
                        else:
                            print(f"  ❌ HTTP {response.status_code} for {url.split('?')[0]}")
                            
                    except Exception as e:
                        print(f"  ⚠️ Error checking {url.split('?')[0]}: {str(e)}")
                        continue
                
                # If we found events this month, add them and reset empty counter
                if month_has_events:
                    events.extend(month_events)
                    consecutive_empty_months = 0
                    print(f"  📅 Total events for {target_date.strftime('%B %Y')}: {len(month_events)}")
                else:
                    consecutive_empty_months += 1
                    print(f"  📭 Month {target_date.strftime('%B %Y')} is empty (consecutive empty: {consecutive_empty_months})")
                
                # Stop if we've had too many consecutive empty months
                if consecutive_empty_months >= max_consecutive_empty:
                    print(f"🛑 Stopping after {max_consecutive_empty} consecutive empty months")
                    break
                
                # Add a small delay to be respectful to the server
                time.sleep(1)
            
            print(f"🏁 Calendar scraping complete. Checked {len(events)} total events across multiple months.")
            return events
            
        except Exception as e:
            print(f"❌ Error in systematic calendar scraping: {str(e)}")
            return events
    
    def _extract_events_from_month_page(self, soup, target_date):
        """Extract events from a specific month's calendar page"""
        events = []
        
        try:
            # Try multiple strategies to find events on the calendar page
            
            # Strategy 1: Look for calendar grid cells
            calendar_selectors = [
                'td[class*="calendar"]',
                'td[class*="day"]',
                'div[class*="calendar-day"]',
                'div[class*="day-cell"]',
                'li[class*="calendar-day"]',
                'div[class*="date-cell"]',
                'td[class*="date"]',
                'div[class*="event-day"]',
                'div[class*="day-events"]'
            ]
            
            for selector in calendar_selectors:
                try:
                    day_cells = soup.select(selector)
                    if day_cells:
                        print(f"    🔍 Found {len(day_cells)} day cells with selector: {selector}")
                        
                        for cell in day_cells:
                            cell_events = self._extract_events_from_calendar_cell(cell, target_date)
                            if cell_events:
                                events.extend(cell_events)
                        
                        if events:
                            break  # Found events, no need to try other selectors
                except Exception as e:
                    print(f"    ⚠️ Error with selector {selector}: {str(e)}")
                    continue
            
            # Strategy 2: Look for event lists
            if not events:
                event_list_selectors = [
                    'ul[class*="events"]',
                    'div[class*="event-list"]',
                    'div[class*="events-list"]',
                    'ul[class*="calendar-events"]',
                    'div[class*="upcoming-events"]',
                    'div[class*="month-events"]',
                    'section[class*="events"]',
                    'div[class*="calendar-content"]'
                ]
                
                for selector in event_list_selectors:
                    try:
                        event_lists = soup.select(selector)
                        if event_lists:
                            print(f"    🔍 Found event list with selector: {selector}")
                            
                            for event_list in event_lists:
                                list_events = self._extract_events_from_list(event_list, target_date)
                                if list_events:
                                    events.extend(list_events)
                            
                            if events:
                                break
                    except Exception as e:
                        print(f"    ⚠️ Error with event list selector {selector}: {str(e)}")
                        continue
            
            # Strategy 3: Look for any elements that might contain event information
            if not events:
                general_selectors = [
                    'div[class*="event"]',
                    'div[class*="calendar"]',
                    'article[class*="event"]',
                    'li[class*="event"]',
                    'div[class*="item"]',
                    'div[class*="entry"]'
                ]
                
                for selector in general_selectors:
                    try:
                        elements = soup.select(selector)
                        if elements:
                            print(f"    🔍 Found {len(elements)} elements with selector: {selector}")
                            
                            for element in elements:
                                element_events = self._extract_events_from_general_element(element, target_date)
                                if element_events:
                                    events.extend(element_events)
                            
                            if events:
                                break
                    except Exception as e:
                        print(f"    ⚠️ Error with general selector {selector}: {str(e)}")
                        continue
            
            # Strategy 4: Fallback to text analysis
            if not events:
                print(f"    🔍 No events found with selectors, trying text analysis...")
                text_events = self._extract_events_from_text(soup)
                if text_events:
                    events.extend(text_events)
                    print(f"    ✅ Text analysis found {len(text_events)} events")
            
        except Exception as e:
            print(f"    ⚠️ Error extracting events from month page: {str(e)}")
        
        return events
    
    def _extract_events_from_calendar_cell(self, cell, month_year):
        """Extract events from a single calendar day cell"""
        events = []
        
        try:
            # Look for event information within the cell
            event_selectors = [
                'div[class*="event"]',
                'span[class*="event"]',
                'a[class*="event"]',
                'div[class*="title"]',
                'span[class*="title"]',
                'a[class*="title"]'
            ]
            
            for selector in event_selectors:
                try:
                    event_elements = cell.select(selector)
                    if event_elements:
                        for element in event_elements:
                            event = self._extract_event_from_calendar_element(element, month_year)
                            if event:
                                events.append(event)
                        break
                except Exception as e:
                    continue
            
            # If no events found with selectors, try to extract from the cell text
            if not events:
                cell_text = cell.get_text(strip=True)
                if cell_text and len(cell_text) > 5:
                    # Try to parse the cell text as an event
                    event = self._parse_cell_text_as_event(cell_text, month_year)
                    if event:
                        events.append(event)
            
        except Exception as e:
            print(f"      ⚠️ Error extracting events from calendar cell: {str(e)}")
        
        return events
    
    def _extract_events_from_list(self, event_list, month_year):
        """Extract events from an event list element"""
        events = []
        
        try:
            # Look for individual event items
            event_item_selectors = [
                'li[class*="event"]',
                'div[class*="event"]',
                'article[class*="event"]',
                'div[class*="item"]',
                'li[class*="item"]'
            ]
            
            for selector in event_item_selectors:
                try:
                    event_items = event_list.select(selector)
                    if event_items:
                        for item in event_items:
                            event = self._extract_event_from_calendar_element(item, month_year)
                            if event:
                                events.append(event)
                        break
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"      ⚠️ Error extracting events from list: {str(e)}")
        
        return events
    
    def _extract_events_from_general_element(self, element, month_year):
        """Extract events from a general element that might contain event information"""
        events = []
        
        try:
            # Try to extract event information from the element
            event = self._extract_event_from_calendar_element(element, month_year)
            if event:
                events.append(event)
            
        except Exception as e:
            print(f"      ⚠️ Error extracting events from general element: {str(e)}")
        
        return events
    
    def _extract_event_from_calendar_element(self, element, month_year):
        """Extract a single event from a calendar element"""
        try:
            # Extract title
            title = None
            title_selectors = [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                '[class*="title"]', '[class*="name"]', '[class*="heading"]',
                'strong', 'b', 'span[class*="title"]', 'a[class*="title"]'
            ]
            
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem and title_elem.get_text(strip=True):
                    title = title_elem.get_text(strip=True)
                    break
            
            if not title:
                # Try to get any text that might be a title
                text_elements = element.find_all(text=True, recursive=True)
                for text in text_elements:
                    text = text.strip()
                    if text and len(text) > 5 and len(text) < 100:
                        # Check if it looks like an event title
                        if not any(word in text.lower() for word in ['am', 'pm', 'edt', 'est', 'from', 'to', 'august', 'september', 'october', 'november', 'december']):
                            if text[0].isupper():  # Starts with capital letter
                                title = text
                                break
            
            if not title:
                return None
            
            # Extract date/time information
            date_time_text = None
            date_selectors = [
                '[class*="date"]', '[class*="time"]', '[class*="datetime"]',
                '[class*="subtitle"]', '[class*="meta"]', '[class*="info"]',
                'time', 'span[class*="date"]', 'div[class*="date"]'
            ]
            
            for selector in date_selectors:
                date_elem = element.select_one(selector)
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    if self._looks_like_datetime(date_text):
                        date_time_text = date_text
                        break
            
            # If no date found in specific elements, search all text
            if not date_time_text:
                all_text = element.get_text()
                # Look for date patterns in the text
                import re
                date_patterns = [
                    r'[A-Za-z]+ \d{1,2},? \d{4}',
                    r'[A-Za-z]+ \d{1,2}',
                    r'\d{1,2}:\d{2}[ap]m',
                    r'from \d{1,2}:\d{2}[ap]m',
                    r'to \d{1,2}:\d{2}[ap]m'
                ]
                
                for pattern in date_patterns:
                    matches = re.findall(pattern, all_text)
                    if matches:
                        # Find the context around the match
                        for match in matches:
                            start_idx = all_text.find(match)
                            if start_idx >= 0:
                                context = all_text[max(0, start_idx-50):start_idx+len(match)+50]
                                if self._looks_like_datetime(context):
                                    date_time_text = context.strip()
                                    break
                        if date_time_text:
                            break
            
            # If still no date found, try to infer from month_year context
            if not date_time_text:
                # Try to find a day number in the element
                day_pattern = r'\b(\d{1,2})\b'
                day_match = re.search(day_pattern, element.get_text())
                if day_match:
                    day = int(day_match.group(1))
                    # Try to construct a date from the month_year context
                    try:
                        from dateutil import parser
                        # Try different date formats
                        date_formats = [
                            f"{month_year} {day}",
                            f"{day} {month_year}",
                            f"{month_year.split()[0]} {day}, {month_year.split()[1]}"
                        ]
                        
                        for date_format in date_formats:
                            try:
                                parsed_date = parser.parse(date_format)
                                # Assume it's an all-day event
                                start_time = parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)
                                end_time = parsed_date.replace(hour=23, minute=59, second=59, microsecond=0)
                                
                                event = {
                                    'title': title,
                                    'start': start_time,
                                    'end': end_time,
                                    'description': f"Event on {date_format}",
                                    'location': 'Antioch Boone',
                                    'all_day': True
                                }
                                
                                return event
                            except:
                                continue
                    except:
                        pass
            
            # If we have date/time text, parse it
            if date_time_text:
                parsed_datetime = self._parse_subsplash_datetime(date_time_text)
                if parsed_datetime:
                    start_time, end_time = parsed_datetime
                    
                    # Extract description
                    description = ""
                    desc_selectors = [
                        '[class*="summary"]', '[class*="description"]', '[class*="details"]',
                        '[class*="content"]', 'p', 'div[class*="text"]'
                    ]
                    
                    for desc_sel in desc_selectors:
                        desc_elem = element.select_one(desc_sel)
                        if desc_elem:
                            desc_text = desc_elem.get_text(strip=True)
                            if desc_text and desc_text != title and len(desc_text) > 10:
                                description = desc_text
                                break
                    
                    event = {
                        'title': title,
                        'start': start_time,
                        'end': end_time,
                        'description': description,
                        'location': 'Antioch Boone',
                        'all_day': False
                    }
                    
                    return event
            
            return None
            
        except Exception as e:
            print(f"        ⚠️ Error extracting event from calendar element: {str(e)}")
            return None
    
    def _parse_cell_text_as_event(self, cell_text, month_year):
        """Try to parse calendar cell text as an event"""
        try:
            # Look for patterns like "Event Name" or "Event Name Time"
            lines = cell_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and len(line) > 5 and len(line) < 100:
                    # Check if it looks like an event title
                    if not any(word in line.lower() for word in ['am', 'pm', 'edt', 'est', 'from', 'to', 'august', 'september', 'october', 'november', 'december']):
                        if line[0].isupper():  # Starts with capital letter
                            # Try to find a day number in the cell text
                            import re
                            day_pattern = r'\b(\d{1,2})\b'
                            day_match = re.search(day_pattern, cell_text)
                            
                            if day_match:
                                day = int(day_match.group(1))
                                try:
                                    from dateutil import parser
                                    # Try to construct a date
                                    date_format = f"{month_year.split()[0]} {day}, {month_year.split()[1]}"
                                    parsed_date = parser.parse(date_format)
                                    
                                    # Assume it's an all-day event
                                    start_time = parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)
                                    end_time = parsed_date.replace(hour=23, minute=59, second=59, microsecond=0)
                                    
                                    event = {
                                        'title': line,
                                        'start': start_time,
                                        'end': end_time,
                                        'description': f"Event on {date_format}",
                                        'location': 'Antioch Boone',
                                        'all_day': True
                                    }
                                    
                                    return event
                                except:
                                    continue
            
            return None
            
        except Exception as e:
            print(f"        ⚠️ Error parsing cell text as event: {str(e)}")
            return None
    
    def _scrape_calendar_with_browser_navigation(self):
        """Use Selenium to navigate month-by-month by clicking the navigation arrows"""
        events = []
        
        try:
            print("🌐 Starting browser-based month-by-month navigation...")
            print("This will actually click the navigation arrows to advance months!")
            
            # Set up Chrome options for headless operation
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            # Initialize the driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            try:
                driver.get("https://antiochboone.com/calendar")
                time.sleep(3) # Give page time to load
                
                consecutive_empty_months = 0
                max_months_to_check = int(os.environ.get('MAX_MONTHS_TO_CHECK', 24)) # Default 2 years
                max_consecutive_empty = int(os.environ.get('MAX_CONSECUTIVE_EMPTY_MONTHS', 3))
                
                for month_count in range(max_months_to_check):
                    current_month_year = driver.find_element(By.CSS_SELECTOR, ".fc-toolbar-title").text.strip()
                    print(f"\n📅 Scraping month: {current_month_year} (Month {month_count + 1}/{max_months_to_check})")
                    
                    # Extract events from the current page
                    page_events = self._extract_events_from_browser_page(driver)
                    
                    if page_events:
                        events.extend(page_events)
                        print(f"  ✅ Found {len(page_events)} events for {current_month_year}")
                        consecutive_empty_months = 0 # Reset counter
                    else:
                        consecutive_empty_months += 1
                        print(f"  📭 No events found for {current_month_year} (empty month #{consecutive_empty_months})")
                    
                    # Check if we should stop
                    if consecutive_empty_months >= max_consecutive_empty:
                        print(f"🛑 Stopping after {max_consecutive_empty} consecutive empty months")
                        break
                    
                    # Find and click the next month arrow (right arrow >)
                    try:
                        # Use the exact FullCalendar selector we found in debug
                        next_arrow = driver.find_element(By.CSS_SELECTOR, "button.fc-next-button")
                        
                        if next_arrow:
                            title = next_arrow.get_attribute('title') or 'Next month'
                            print(f"  ✅ Found next month button: {title}")
                            print(f"  ➡️ Clicking next month arrow...")
                            
                            # Try multiple click strategies
                            click_success = False
                            
                            # Strategy 1: JavaScript click
                            try:
                                driver.execute_script("arguments[0].click();", next_arrow)
                                click_success = True
                                print("  ✅ Clicked via JavaScript")
                            except Exception as js_error:
                                print(f"  ⚠️ JavaScript click failed: {str(js_error)}")
                            
                            # Strategy 2: Scroll into view and click
                            if not click_success:
                                try:
                                    driver.execute_script("arguments[0].scrollIntoView(true);", next_arrow)
                                    time.sleep(1)
                                    next_arrow.click()
                                    click_success = True
                                    print("  ✅ Clicked after scrolling into view")
                                except Exception as scroll_error:
                                    print(f"  ⚠️ Scroll + click failed: {str(scroll_error)}")
                            
                            # Strategy 3: Wait for element to be clickable
                            if not click_success:
                                try:
                                    WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fc-next-button"))
                                    )
                                    next_arrow.click()
                                    click_success = True
                                    print("  ✅ Clicked after waiting for clickable")
                                except Exception as wait_error:
                                    print(f"  ⚠️ Wait + click failed: {str(wait_error)}")
                            
                            if click_success:
                                # Wait for the new month to load
                                time.sleep(3)  # Wait for content to render
                                
                                # Verify month actually changed
                                new_month_year = driver.find_element(By.CSS_SELECTOR, ".fc-toolbar-title").text.strip()
                                if new_month_year != current_month_year:
                                    print(f"  ✅ Month advanced from '{current_month_year}' to '{new_month_year}'")
                                else:
                                    print(f"  ⚠️ Month didn't change, still showing '{current_month_year}'")
                                    # Try one more time with a longer wait
                                    time.sleep(2)
                                    new_month_year = driver.find_element(By.CSS_SELECTOR, ".fc-toolbar-title").text.strip()
                                    if new_month_year != current_month_year:
                                        print(f"  ✅ Month advanced after longer wait: '{new_month_year}'")
                                    else:
                                        print(f"  ❌ Month still didn't change, navigation may be stuck")
                                        break
                            else:
                                raise Exception("All click strategies failed")
                            
                        else:
                            raise Exception("Next month button not found")
                        
                    except Exception as e:
                        print(f"  ❌ Could not navigate to next month: {str(e)}")
                        print("  🔍 Trying alternative navigation methods...")
                        
                        # Try alternative navigation methods
                        alt_nav_success = self._try_alternative_browser_navigation(driver)
                        if not alt_nav_success:
                            print("  ❌ No navigation method worked, stopping")
                            break
                
                print(f"🏁 Browser navigation complete. Found {len(events)} total events across {month_count + 1} months.")
                
            finally:
                driver.quit()
                print("🌐 Browser closed")
        
        except Exception as e:
            print(f"❌ Error in browser-based navigation: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return events
    
    def _extract_events_from_browser_page(self, driver):
        """Extract events from the current browser page"""
        events = []
        
        try:
            # Get the page source and parse with BeautifulSoup
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Look for event elements on the page
            event_selectors = [
                'div[class*="event"]',
                'div[class*="calendar-event"]',
                'td[class*="event"]',
                'li[class*="event"]',
                'div[class*="day-event"]',
                'span[class*="event"]',
                'a[class*="event"]'
            ]
            
            for selector in event_selectors:
                try:
                    event_elements = soup.select(selector)
                    if event_elements:
                        print(f"    🔍 Found {len(event_elements)} event elements with selector: {selector}")
                        
                        for element in event_elements:
                            event = self._extract_event_from_browser_element(element, driver)
                            if event:
                                # Check for duplicates before adding
                                if not self._is_duplicate_event(event, events):
                                    events.append(event)
                        
                        if events:
                            break  # Found events, no need to try other selectors
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"    ⚠️ Error extracting events from browser page: {str(e)}")
        
        return events
    
    def _extract_event_from_browser_element(self, element, driver):
        """Extract event information from a browser element"""
        try:
            # Get the element text
            event_text = element.get_text(strip=True)
            if not event_text or len(event_text) < 5:
                return None
            
            # Try to extract date information from the element or its context
            event_date = self._extract_event_date_from_element(element, driver)
            
            # Try to parse the event text
            parsed_event = self._parse_event_text(event_text)
            if parsed_event:
                # Combine parsed text with extracted date
                event = {
                    "title": parsed_event.get("title", event_text),
                    "time": parsed_event.get("time"),
                    "date": event_date,
                    "source": "browser_calendar",
                    "raw_text": event_text
                }
                return event
            
        except Exception as e:
            print(f"      ⚠️ Error extracting event from browser element: {str(e)}")
        
        return None
    
    def _extract_event_date_from_element(self, element, driver):
        """Extract the actual event date from the element or its context"""
        try:
            # Method 1: Look for date attributes
            date_attrs = ['data-date', 'data-event-date', 'title', 'aria-label']
            for attr in date_attrs:
                date_value = element.get(attr)
                if date_value:
                    # Try to parse the date
                    parsed_date = self._parse_date_string(date_value)
                    if parsed_date:
                        return parsed_date
            
            # Method 2: Look for parent elements with date information
            parent = element.parent
            for _ in range(3):  # Check up to 3 levels up
                if parent:
                    # Look for date-related classes or attributes
                    if parent.get('class'):
                        for class_name in parent.get('class'):
                            if 'date' in class_name.lower() or 'day' in class_name.lower():
                                date_text = parent.get_text(strip=True)
                                parsed_date = self._parse_date_string(date_text)
                                if parsed_date:
                                    return parsed_date
                    parent = parent.parent
            
            # Method 3: Look for the current month/year from the calendar header
            try:
                month_year_text = driver.find_element(By.CSS_SELECTOR, ".fc-toolbar-title").text.strip()
                # Extract month and year from the header
                parsed_date = self._parse_month_year_string(month_year_text)
                if parsed_date:
                    return parsed_date
            except:
                pass
            
        except Exception as e:
            print(f"        ⚠️ Error extracting date from element: {str(e)}")
        
        return None
    
    def _parse_date_string(self, date_string):
        """Parse various date string formats"""
        try:
            if not date_string:
                return None
            
            # Common date patterns
            date_patterns = [
                r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
                r'(\d{1,2})-(\d{1,2})-(\d{4})',  # MM-DD-YYYY
                r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',  # Month DD, YYYY
                r'(\d{1,2})\s+(\w+)\s+(\d{4})',  # DD Month YYYY
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_string)
                if match:
                    if len(match.groups()) == 3:
                        if pattern == r'(\w+)\s+(\d{1,2}),?\s+(\d{4})':
                            # Month DD, YYYY format
                            month_str, day, year = match.groups()
                            month = self._month_name_to_number(month_str)
                            if month:
                                return datetime(int(year), month, int(day))
                        elif pattern == r'(\d{1,2})\s+(\w+)\s+(\d{4})':
                            # DD Month YYYY format
                            day, month_str, year = match.groups()
                            month = self._month_name_to_number(month_str)
                            if month:
                                return datetime(int(year), month, int(day))
                        else:
                            # MM/DD/YYYY or MM-DD-YYYY format
                            month, day, year = match.groups()
                            return datetime(int(year), int(month), int(day))
            
            # Try direct parsing with dateutil
            try:
                return parser.parse(date_string, fuzzy=True)
            except:
                pass
                
        except Exception as e:
            print(f"          ⚠️ Error parsing date string '{date_string}': {str(e)}")
        
        return None
    
    def _parse_month_year_string(self, month_year_string):
        """Parse month year strings like 'August 2025'"""
        try:
            if not month_year_string:
                return None
            
            # Pattern for "Month YYYY" format
            pattern = r'(\w+)\s+(\d{4})'
            match = re.search(pattern, month_year_string)
            if match:
                month_str, year = match.groups()
                month = self._month_name_to_number(month_str)
                if month:
                    # Return first day of the month
                    return datetime(int(year), month, 1)
                    
        except Exception as e:
            print(f"          ⚠️ Error parsing month year string '{month_year_string}': {str(e)}")
        
        return None
    
    def _month_name_to_number(self, month_name):
        """Convert month name to month number"""
        month_map = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
        return month_map.get(month_name.lower())
    
    def _is_duplicate_event(self, new_event, existing_events):
        """Check if an event is a duplicate based on title and date"""
        try:
            if not new_event or not existing_events:
                return False
            
            new_title = new_event.get('title', '').strip().lower()
            new_date = new_event.get('date')
            
            if not new_title or not new_date:
                return False
            
            for existing_event in existing_events:
                existing_title = existing_event.get('title', '').strip().lower()
                existing_date = existing_event.get('date')
                
                if (new_title == existing_title and 
                    new_date and existing_date and 
                    new_date.date() == existing_date.date()):
                    return True
            
            return False
            
        except Exception as e:
            print(f"        ⚠️ Error checking for duplicates: {str(e)}")
            return False
    
    def _try_alternative_browser_navigation(self, driver):
        """Try alternative methods to navigate to the next month"""
        try:
            # Method 1: Look for month/year dropdowns
            month_selectors = [
                'select[name*="month"]',
                'select[id*="month"]',
                'input[name*="month"]',
                'input[id*="month"]'
            ]
            
            for selector in month_selectors:
                try:
                    month_element = driver.find_element(By.CSS_SELECTOR, selector)
                    # Try to select next month
                    current_month = month_element.get_attribute('value') or '1'
                    next_month = str((int(current_month) % 12) + 1)
                    month_element.clear()
                    month_element.send_keys(next_month)
                    return True
                except:
                    continue
            
            # Method 2: Look for keyboard navigation
            try:
                from selenium.webdriver.common.keys import Keys
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ARROW_RIGHT)
                time.sleep(1)
                return True
            except:
                pass
            
            return False
            
        except Exception as e:
            print(f"      ⚠️ Error in alternative browser navigation: {str(e)}")
            return False
    
    def _parse_event_text(self, event_text):
        """Parse event text to extract event information"""
        try:
            # Simple parsing for now - can be enhanced
            if not event_text or len(event_text) < 5:
                return None
            
            # Try to extract time and title
            # Common patterns: "10:30a Sunday Service", "5:15p Prayer Set"
            time_pattern = r'(\d{1,2}:\d{2}[ap])\s*(.+)'
            match = re.search(time_pattern, event_text)
            
            if match:
                time_str = match.group(1)
                title = match.group(2).strip()
                
                # Create a basic event structure
                event = {
                    'title': title,
                    'time': time_str,
                    'date': datetime.now(),  # Will be set by caller
                    'source': 'browser_navigation'
                }
                return event
            
            # If no time pattern, just use the text as title
            event = {
                'title': event_text,
                'time': 'TBD',
                'date': datetime.now(),  # Will be set by caller
                'source': 'browser_navigation'
            }
            return event
            
        except Exception as e:
            print(f"      ⚠️ Error parsing event text '{event_text}': {str(e)}")
            return None
    
    def _try_alternative_calendar_navigation(self):
        """Try alternative approaches to access calendar data"""
        events = []
        
        try:
            # Try different base URLs and approaches
            alternative_urls = [
                "https://antiochboone.com/events",
                "https://antiochboone.com/calendar/events",
                "https://antiochboone.com/upcoming-events",
                "https://antiochboone.com/all-events",
                "https://antiochboone.com/calendar/list",
                "https://antiochboone.com/calendar/grid",
                "https://antiochboone.com/calendar/monthly",
                "https://antiochboone.com/calendar/yearly",
                # Try Subsplash-specific URLs
                "https://subsplash.com/+wrmm/lb/ca/+pysr4r6",
                "https://subsplash.com/+wrmm/lb/ca/+pysr4r6/events",
                "https://subsplash.com/+wrmm/lb/ca/+pysr4r6/calendar",
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            print("  🔍 Trying alternative calendar URLs...")
            
            for url in alternative_urls:
                try:
                    response = requests.get(url, headers=headers, timeout=30)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Try to extract events from this alternative page
                        alt_page_events = self._extract_events_from_alternative_page(soup, url)
                        
                        if alt_page_events:
                            events.extend(alt_page_events)
                            print(f"    ✅ {url.split('/')[-1]}: Found {len(alt_page_events)} events")
                        else:
                            print(f"    ⚠️ {url.split('/')[-1]}: No events found")
                    else:
                        print(f"    ❌ {url.split('/')[-1]}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"    ⚠️ Error with {url.split('/')[-1]}: {str(e)}")
                    continue
                
                # Small delay between requests
                time.sleep(0.5)
            
            # Try to find and parse any embedded calendar data
            print("  🔍 Looking for embedded calendar data...")
            embedded_events = self._find_embedded_calendar_data()
            if embedded_events:
                events.extend(embedded_events)
                print(f"    ✅ Embedded data: Found {len(embedded_events)} events")
            
            return events
            
        except Exception as e:
            print(f"❌ Error in alternative calendar navigation: {str(e)}")
            return events
    
    def _extract_events_from_alternative_page(self, soup, url):
        """Extract events from alternative calendar pages"""
        events = []
        
        try:
            # Try different event extraction strategies for alternative pages
            event_selectors = [
                # Common event selectors
                'div[class*="event"]',
                'div[class*="item"]',
                'div[class*="entry"]',
                'div[class*="post"]',
                'div[class*="card"]',
                'div[class*="listing"]',
                'li[class*="event"]',
                'li[class*="item"]',
                'article[class*="event"]',
                'article[class*="item"]',
                # Subsplash-specific selectors
                'div[class*="kit"]',
                'div[class*="subsplash"]',
                'div[class*="wrmm"]',
                # Generic content selectors
                'div[class*="content"]',
                'div[class*="main"]',
                'div[class*="container"]',
            ]
            
            for selector in event_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"      🔍 Found {len(elements)} elements with selector: {selector}")
                    
                    for element in elements:
                        event = self._extract_event_from_alternative_element(element, url)
                        if event:
                            events.append(event)
                    
                    if events:
                        break  # Found events with this selector
            
            # If no events found with selectors, try text-based extraction
            if not events:
                print("      🔍 Trying text-based extraction...")
                text_events = self._extract_events_from_text(soup.get_text())
                if text_events:
                    events.extend(text_events)
            
            return events
            
        except Exception as e:
            print(f"      ⚠️ Error extracting events from alternative page: {str(e)}")
            return events
    
    def _extract_event_from_alternative_element(self, element, url):
        """Extract event details from alternative page elements"""
        try:
            # Try to find title
            title = None
            title_selectors = [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                '[class*="title"]', '[class*="name"]', '[class*="heading"]',
                'a[class*="title"]', 'span[class*="title"]'
            ]
            
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem and title_elem.get_text().strip():
                    title = title_elem.get_text().strip()
                    break
            
            # Try to find date/time
            date_time = None
            date_selectors = [
                '[class*="date"]', '[class*="time"]', '[class*="datetime"]',
                '[class*="when"]', '[class*="schedule"]', '[class*="calendar"]',
                'time', '[datetime]', '[data-date]', '[data-time]'
            ]
            
            for selector in date_selectors:
                date_elem = element.select_one(selector)
                if date_elem:
                    # Try to get datetime attribute first
                    datetime_attr = date_elem.get('datetime') or date_elem.get('data-date') or date_elem.get('data-time')
                    if datetime_attr:
                        date_time = datetime_attr
                        break
                    # Fall back to text content
                    elif date_elem.get_text().strip():
                        date_time = date_elem.get_text().strip()
                        break
            
            # Try to find description
            description = None
            desc_selectors = [
                '[class*="description"]', '[class*="summary"]', '[class*="content"]',
                '[class*="details"]', '[class*="text"]', 'p', 'span'
            ]
            
            for selector in desc_selectors:
                desc_elem = element.select_one(selector)
                if desc_elem and desc_elem.get_text().strip():
                    desc_text = desc_elem.get_text().strip()
                    if desc_text and desc_text != title:
                        description = desc_text
                        break
            
            # If we have at least a title, create an event
            if title:
                # Try to parse the date/time
                start_time = None
                end_time = None
                
                if date_time:
                    parsed_time = self._parse_subsplash_datetime(date_time)
                    if parsed_time:
                        start_time = parsed_time
                        # Assume 1 hour duration if no end time specified
                        end_time = start_time + timedelta(hours=1)
                
                # If no date/time found, try to extract from the element's text
                if not start_time:
                    element_text = element.get_text()
                    parsed_time = self._parse_subsplash_datetime(element_text)
                    if parsed_time:
                        start_time = parsed_time
                        end_time = start_time + timedelta(hours=1)
                
                if start_time:
                    return {
                        'title': title,
                        'start': start_time,
                        'end': end_time,
                        'description': description,
                        'source': f"Alternative page: {url}"
                    }
            
            return None
            
        except Exception as e:
            print(f"        ⚠️ Error extracting event from alternative element: {str(e)}")
            return None
    
    def _find_embedded_calendar_data(self):
        """Try to find embedded calendar data in the page"""
        events = []
        
        try:
            # Try to find any embedded calendar data
            embedded_urls = [
                "https://antiochboone.com/calendar/feed",
                "https://antiochboone.com/calendar/rss",
                "https://antiochboone.com/events/feed",
                "https://antiochboone.com/events/rss",
                "https://antiochboone.com/calendar.ics",
                "https://antiochboone.com/events.ics",
                "https://antiochboone.com/calendar.json",
                "https://antiochboone.com/events.json",
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/calendar,application/json,application/rss+xml,text/xml,*/*',
            }
            
            for url in embedded_urls:
                try:
                    response = requests.get(url, headers=headers, timeout=30)
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        
                        if 'json' in content_type:
                            # Parse JSON calendar data
                            try:
                                json_data = response.json()
                                json_events = self._parse_json_events(json_data)
                                if json_events:
                                    events.extend(json_events)
                                    print(f"        ✅ Found {len(json_events)} events in JSON feed: {url.split('/')[-1]}")
                            except Exception as e:
                                print(f"        ⚠️ Error parsing JSON from {url.split('/')[-1]}: {str(e)}")
                        
                        elif 'xml' in content_type or 'rss' in content_type:
                            # Parse XML/RSS calendar data
                            try:
                                soup = BeautifulSoup(response.content, 'xml')
                                xml_events = self._parse_xml_calendar_data(soup)
                                if xml_events:
                                    events.extend(xml_events)
                                    print(f"        ✅ Found {len(xml_events)} events in XML feed: {url.split('/')[-1]}")
                            except Exception as e:
                                print(f"        ⚠️ Error parsing XML from {url.split('/')[-1]}: {str(e)}")
                        
                        elif 'calendar' in content_type or url.endswith('.ics'):
                            # Parse iCal calendar data
                            try:
                                ical_events = self._parse_ical_calendar_data(response.text)
                                if ical_events:
                                    events.extend(ical_events)
                                    print(f"        ✅ Found {len(ical_events)} events in iCal feed: {url.split('/')[-1]}")
                            except Exception as e:
                                print(f"        ⚠️ Error parsing iCal from {url.split('/')[-1]}: {str(e)}")
                        
                        else:
                            print(f"        ⚠️ Unknown content type for {url.split('/')[-1]}: {content_type}")
                    
                    else:
                        print(f"        ❌ HTTP {response.status_code} for {url.split('/')[-1]}")
                        
                except Exception as e:
                    print(f"        ⚠️ Error checking {url.split('/')[-1]}: {str(e)}")
                    continue
            
            return events
            
        except Exception as e:
            print(f"❌ Error finding embedded calendar data: {str(e)}")
            return events
    
    def _parse_xml_calendar_data(self, soup):
        """Parse XML/RSS calendar data"""
        events = []
        
        try:
            # Try to find items in RSS feeds
            items = soup.find_all(['item', 'entry', 'event'])
            
            for item in items:
                try:
                    # Extract title
                    title_elem = item.find(['title', 'name', 'summary'])
                    title = title_elem.get_text().strip() if title_elem else None
                    
                    # Extract date/time
                    date_elem = item.find(['pubdate', 'date', 'datetime', 'time'])
                    date_text = None
                    if date_elem:
                        date_text = date_elem.get('datetime') or date_elem.get_text().strip()
                    
                    # Extract description
                    desc_elem = item.find(['description', 'summary', 'content'])
                    description = desc_elem.get_text().strip() if desc_elem else None
                    
                    if title and date_text:
                        # Try to parse the date
                        try:
                            start_time = parser.parse(date_text)
                            end_time = start_time + timedelta(hours=1)
                            
                            events.append({
                                'title': title,
                                'start': start_time,
                                'end': end_time,
                                'description': description,
                                'source': 'XML/RSS feed'
                            })
                        except Exception as e:
                            print(f"          ⚠️ Could not parse date '{date_text}': {str(e)}")
                            continue
                
                except Exception as e:
                    print(f"          ⚠️ Error parsing XML item: {str(e)}")
                    continue
            
            return events
            
        except Exception as e:
            print(f"❌ Error parsing XML calendar data: {str(e)}")
            return events
    
    def _parse_ical_calendar_data(self, ical_text):
        """Parse iCal calendar data"""
        events = []
        
        try:
            # Simple iCal parsing (for basic VEVENT entries)
            lines = ical_text.split('\n')
            current_event = {}
            in_event = False
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('BEGIN:VEVENT'):
                    current_event = {}
                    in_event = True
                elif line.startswith('END:VEVENT'):
                    if current_event.get('title') and current_event.get('start'):
                        try:
                            start_time = parser.parse(current_event['start'])
                            end_time = parser.parse(current_event['end']) if current_event.get('end') else start_time + timedelta(hours=1)
                            
                            events.append({
                                'title': current_event['title'],
                                'start': start_time,
                                'end': end_time,
                                'description': current_event.get('description'),
                                'source': 'iCal feed'
                            })
                        except Exception as e:
                            print(f"          ⚠️ Could not parse iCal event dates: {str(e)}")
                            continue
                    
                    in_event = False
                    current_event = {}
                
                elif in_event and ':' in line:
                    key, value = line.split(':', 1)
                    key = key.upper()
                    
                    if key == 'SUMMARY':
                        current_event['title'] = value
                    elif key == 'DTSTART':
                        current_event['start'] = value
                    elif key == 'DTEND':
                        current_event['end'] = value
                    elif key == 'DESCRIPTION':
                        current_event['description'] = value
            
            return events
            
        except Exception as e:
            print(f"❌ Error parsing iCal calendar data: {str(e)}")
            return events

    def _simulate_browser_behavior(self, url):
        """Simulate browser behavior to trigger dynamic loading"""
        events = []
        
        try:
            print("          🔍 Simulating browser behavior...")
            
            # Try different user agent strings
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            
            for user_agent in user_agents:
                try:
                    headers = {
                        'User-Agent': user_agent,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Cache-Control': 'max-age=0'
                    }
                    
                    response = requests.get(url, headers=headers, timeout=30)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Try to extract events with this user agent
                        page_events = self._extract_events_from_page(soup)
                        if page_events:
                            events.extend(page_events)
                            print(f"          ✅ User agent {user_agent[:20]}...: Found {len(page_events)} events")
                            break
                        else:
                            print(f"          ⚠️ User agent {user_agent[:20]}...: No events found")
                    else:
                        print(f"          ❌ HTTP {response.status_code} with user agent {user_agent[:20]}...")
                        
                except Exception as e:
                    print(f"          ⚠️ Error with user agent {user_agent[:20]}...: {str(e)}")
                    continue
            
            # Try to simulate scrolling/loading more content
            if not events:
                print("          🔍 Trying to simulate scrolling/loading more...")
                try:
                    # Try different scroll parameters
                    scroll_urls = [
                        url + "&scroll=1",
                        url + "&load_more=1",
                        url + "&page=2",
                        url + "&offset=20",
                        url + "&start=20"
                    ]
                    
                    for scroll_url in scroll_urls:
                        try:
                            response = requests.get(scroll_url, headers=headers, timeout=30)
                            if response.status_code == 200:
                                soup = BeautifulSoup(response.content, 'html.parser')
                                scroll_events = self._extract_events_from_page(soup)
                                if scroll_events:
                                    events.extend(scroll_events)
                                    print(f"          ✅ Scroll URL {scroll_url.split('?')[-1]}: Found {len(scroll_events)} events")
                                    break
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    print(f"          ⚠️ Error simulating scrolling: {str(e)}")
            
            return events
            
        except Exception as e:
            print(f"❌ Error simulating browser behavior: {str(e)}")
            return events

def main():
    """Main function for GitHub Actions"""
    if not GOOGLE_CALENDAR_ID or not SUBSPLASH_EMBED_URL:
        print("❌ Missing required environment variables")
        print(f"GOOGLE_CALENDAR_ID: {GOOGLE_CALENDAR_ID}")
        print(f"SUBSPLASH_EMBED_URL: {SUBSPLASH_EMBED_URL}")
        exit(1)
    
    service = SubsplashSyncService()
    success = service.run_sync()
    
    if success:
        print("🎉 Sync completed successfully!")
        exit(0)
    else:
        print("💥 Sync failed!")
        exit(1)

if __name__ == "__main__":
    main()