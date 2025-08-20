#!/usr/bin/env python3
"""
Subsplash to Google Calendar Sync Script
This script runs automatically via GitHub Actions to sync events from Subsplash to Google Calendar.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time
from dateutil import parser

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
                subsplash_url.replace("?embed", "&limit=100"),
                subsplash_url.replace("?embed", "&limit=200"),
                subsplash_url.replace("?embed", "&limit=500"),
                subsplash_url.replace("?embed", "&show_all=1"),
                subsplash_url.replace("?embed", "&include_past=1"),
                subsplash_url.replace("?embed", "&include_future=1"),
                subsplash_url.replace("?embed", "&future_events=1"),
                subsplash_url.replace("?embed", "&all_events=1"),
                subsplash_url.replace("?embed", "&range=all"),
                subsplash_url.replace("?embed", "&range=future"),
                subsplash_url.replace("?embed", "&range=year"),
                subsplash_url.replace("?embed", "&range=6months"),
                subsplash_url.replace("?embed", "&range=12months"),
                subsplash_url.replace("?embed", "&months_ahead=6"),
                subsplash_url.replace("?embed", "&months_ahead=12"),
                subsplash_url.replace("?embed", "&months_ahead=24"),
                subsplash_url.replace("?embed", "&start_date=today"),
                subsplash_url.replace("?embed", "&end_date=2026-12-31"),
                subsplash_url.replace("?embed", "&end_date=2027-12-31"),
                subsplash_url.replace("?embed", "&end_date=2028-12-31"),
                subsplash_url.replace("?embed", "&timeframe=all"),
                subsplash_url.replace("?embed", "&timeframe=future"),
                subsplash_url.replace("?embed", "&timeframe=year"),
                subsplash_url.replace("?embed", "&timeframe=extended"),
                subsplash_url.replace("?embed", "&load_more=1"),
                subsplash_url.replace("?embed", "&expand=1"),
                subsplash_url.replace("?embed", "&full=1"),
                subsplash_url.replace("?embed", "&complete=1"),
                subsplash_url.replace("?embed", "&all=1")
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
            from bs4 import BeautifulSoup
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