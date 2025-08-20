import requests
from bs4 import BeautifulSoup
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class SubsplashExtractor:
    """Extracts calendar data from Subsplash embed codes and pages"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.last_extraction = None
        self.extracted_events = []
        
    def extract_from_embed_code(self, embed_code: str) -> List[Dict]:
        """
        Extract calendar data from a Subsplash embed code
        
        Args:
            embed_code: The HTML embed code from Subsplash
            
        Returns:
            List of extracted events
        """
        try:
            # Parse the embed code to extract the calendar ID
            calendar_id = self._parse_embed_code(embed_code)
            if not calendar_id:
                raise ValueError("Could not extract calendar ID from embed code")
            
            # Extract events from the Subsplash calendar
            events = self._extract_calendar_events(calendar_id)
            
            # Update internal state
            self.extracted_events = events
            self.last_extraction = datetime.now()
            
            logger.info(f"Successfully extracted {len(events)} events from Subsplash calendar {calendar_id}")
            return events
            
        except Exception as e:
            logger.error(f"Failed to extract from embed code: {str(e)}")
            raise
    
    def _parse_embed_code(self, embed_code: str) -> Optional[str]:
        """Parse embed code to extract calendar identifier"""
        try:
            # Look for the calendar ID in the embed code
            # Pattern: +wrmm/lb/ca/+pysr4r6?embed
            pattern = r'\+wrmm/lb/ca/\+([a-zA-Z0-9]+)\?embed'
            match = re.search(pattern, embed_code)
            
            if match:
                return match.group(1)
            
            # Alternative pattern for different embed formats
            pattern2 = r'subsplashEmbed\s*\(\s*["\']([^"\']+)["\']'
            match2 = re.search(pattern2, embed_code)
            
            if match2:
                embed_url = match2.group(1)
                # Extract ID from URL
                id_match = re.search(r'\+([a-zA-Z0-9]+)', embed_url)
                if id_match:
                    return id_match.group(1)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse embed code: {str(e)}")
            return None
    
    def _extract_calendar_events(self, calendar_id: str) -> List[Dict]:
        """Extract events from Subsplash calendar using the calendar ID"""
        try:
            # Construct the calendar URL
            calendar_url = f"https://subsplash.com/+wrmm/lb/ca/+{calendar_id}"
            
            # Fetch the calendar page
            response = self.session.get(calendar_url)
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract events from the page
            events = self._parse_calendar_page(soup)
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to extract calendar events: {str(e)}")
            raise
    
    def _parse_calendar_page(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse the calendar page HTML to extract event information"""
        events = []
        
        try:
            # Look for event containers - this will need to be customized based on Subsplash's actual HTML structure
            event_containers = soup.find_all(['div', 'article'], class_=re.compile(r'event|calendar-item|entry'))
            
            for container in event_containers:
                event = self._extract_single_event(container)
                if event:
                    events.append(event)
            
            # If no events found with standard selectors, try alternative approaches
            if not events:
                events = self._extract_events_alternative(soup)
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to parse calendar page: {str(e)}")
            return []
    
    def _extract_single_event(self, container) -> Optional[Dict]:
        """Extract information from a single event container"""
        try:
            event = {}
            
            # Extract title
            title_elem = container.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'title|heading'))
            if title_elem:
                event['title'] = title_elem.get_text(strip=True)
            
            # Extract date/time
            date_elem = container.find(['time', 'span', 'div'], class_=re.compile(r'date|time|datetime'))
            if date_elem:
                event['datetime'] = self._parse_datetime(date_elem)
            
            # Extract description
            desc_elem = container.find(['p', 'div'], class_=re.compile(r'description|summary|content'))
            if desc_elem:
                event['description'] = desc_elem.get_text(strip=True)
            
            # Extract location
            location_elem = container.find(['span', 'div'], class_=re.compile(r'location|venue|address'))
            if location_elem:
                event['location'] = location_elem.get_text(strip=True)
            
            # Extract link
            link_elem = container.find('a', href=True)
            if link_elem:
                event['link'] = link_elem['href']
            
            # Only return event if we have at least a title and datetime
            if event.get('title') and event.get('datetime'):
                return event
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract single event: {str(e)}")
            return None
    
    def _extract_events_alternative(self, soup: BeautifulSoup) -> List[Dict]:
        """Alternative method to extract events if standard parsing fails"""
        events = []
        
        try:
            # Look for JSON-LD structured data
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'Event':
                        event = self._parse_json_ld_event(data)
                        if event:
                            events.append(event)
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and item.get('@type') == 'Event':
                                event = self._parse_json_ld_event(item)
                                if event:
                                    events.append(event)
                except json.JSONDecodeError:
                    continue
            
            # Look for microdata
            event_elements = soup.find_all(attrs={'itemtype': re.compile(r'Event', re.I)})
            for elem in event_elements:
                event = self._parse_microdata_event(elem)
                if event:
                    events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Alternative event extraction failed: {str(e)}")
            return []
    
    def _parse_json_ld_event(self, data: Dict) -> Optional[Dict]:
        """Parse JSON-LD structured event data"""
        try:
            event = {
                'title': data.get('name', ''),
                'description': data.get('description', ''),
                'location': data.get('location', {}).get('name', '') if isinstance(data.get('location'), dict) else str(data.get('location', '')),
                'link': data.get('url', ''),
                'datetime': self._parse_iso_datetime(data.get('startDate', ''))
            }
            
            if event['title'] and event['datetime']:
                return event
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse JSON-LD event: {str(e)}")
            return None
    
    def _parse_microdata_event(self, elem) -> Optional[Dict]:
        """Parse microdata event information"""
        try:
            event = {}
            
            title_elem = elem.find(attrs={'itemprop': 'name'})
            if title_elem:
                event['title'] = title_elem.get_text(strip=True)
            
            desc_elem = elem.find(attrs={'itemprop': 'description'})
            if desc_elem:
                event['description'] = desc_elem.get_text(strip=True)
            
            start_elem = elem.find(attrs={'itemprop': 'startDate'})
            if start_elem:
                event['datetime'] = self._parse_datetime(start_elem)
            
            location_elem = elem.find(attrs={'itemprop': 'location'})
            if location_elem:
                event['location'] = location_elem.get_text(strip=True)
            
            if event.get('title') and event.get('datetime'):
                return event
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse microdata event: {str(e)}")
            return None
    
    def _parse_datetime(self, elem) -> Optional[datetime]:
        """Parse datetime from various HTML elements"""
        try:
            # Check for datetime attribute first
            if elem.get('datetime'):
                return self._parse_iso_datetime(elem['datetime'])
            
            # Check for content attribute
            if elem.get('content'):
                return self._parse_iso_datetime(elem['content'])
            
            # Parse text content
            text = elem.get_text(strip=True)
            if text:
                return self._parse_text_datetime(text)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse datetime: {str(e)}")
            return None
    
    def _parse_iso_datetime(self, iso_string: str) -> Optional[datetime]:
        """Parse ISO format datetime string"""
        try:
            # Try various ISO formats
            formats = [
                '%Y-%m-%dT%H:%M:%S%z',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(iso_string, fmt)
                except ValueError:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse ISO datetime: {str(e)}")
            return None
    
    def _parse_text_datetime(self, text: str) -> Optional[datetime]:
        """Parse datetime from text content"""
        try:
            # This is a simplified parser - you may need to enhance it based on Subsplash's date format
            # Common patterns
            patterns = [
                r'(\d{1,2})/(\d{1,2})/(\d{4})',
                r'(\d{4})-(\d{1,2})-(\d{1,2})',
                r'(\w+)\s+(\d{1,2}),?\s+(\d{4})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    if len(match.groups()) == 3:
                        month, day, year = match.groups()
                        try:
                            return datetime(int(year), int(month), int(day))
                        except ValueError:
                            continue
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse text datetime: {str(e)}")
            return None
    
    def get_status(self) -> Dict:
        """Get the current status of the extractor"""
        return {
            'last_extraction': self.last_extraction.isoformat() if self.last_extraction else None,
            'total_events_extracted': len(self.extracted_events),
            'status': 'active'
        }
    
    def get_extracted_events(self) -> List[Dict]:
        """Get the last extracted events"""
        return self.extracted_events.copy()
