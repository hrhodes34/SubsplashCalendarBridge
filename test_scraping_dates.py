#!/usr/bin/env python3
"""
Test script to verify Subsplash date scraping
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def test_subsplash_date_extraction():
    """Test scraping a Subsplash page to see what dates are found"""
    
    print("🔍 Testing Subsplash Date Extraction")
    print("=" * 50)
    
    # Test URLs from your calendar config
    test_urls = [
        "https://antiochboone.com/calendar-bam",
        "https://antiochboone.com/calendar-kids", 
        "https://antiochboone.com/calendar-prayer"
    ]
    
    for url in test_urls:
        print(f"\n📅 Testing: {url}")
        print("-" * 40)
        
        try:
            # Make request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code != 200:
                print(f"❌ Failed to fetch: {response.status_code}")
                continue
                
            print(f"✅ Page fetched successfully")
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for date-related elements
            date_elements = []
            
            # Common date selectors
            date_selectors = [
                '.fc-day-header',           # FullCalendar day headers
                '.fc-day-number',           # FullCalendar day numbers
                '.event-date',              # Generic event date
                '.date',                    # Generic date
                '[data-date]',              # Elements with data-date attribute
                '.fc-event-time',           # FullCalendar event times
                '.fc-event-title',          # FullCalendar event titles
                '.event-title',             # Generic event titles
                '.fc-toolbar-title'         # FullCalendar month/year title
            ]
            
            for selector in date_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 0:
                        date_elements.append({
                            'selector': selector,
                            'text': text,
                            'html': str(element)[:100] + '...' if len(str(element)) > 100 else str(element)
                        })
            
            print(f"📊 Found {len(date_elements)} potential date elements:")
            
            # Show first 10 elements
            for i, elem in enumerate(date_elements[:10]):
                print(f"  {i+1}. {elem['selector']}: '{elem['text']}'")
            
            # Look for month/year information
            month_year_elements = soup.find_all(text=re.compile(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}'))
            if month_year_elements:
                print(f"\n📅 Month/Year found: {month_year_elements[0]}")
            
            # Look for specific date patterns
            date_patterns = [
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b',
                r'\b\d{1,2}/\d{1,2}/\d{4}\b',
                r'\b\d{4}-\d{2}-\d{2}\b',
                r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b'
            ]
            
            print(f"\n🔍 Looking for date patterns:")
            for pattern in date_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                if matches:
                    print(f"  Pattern '{pattern}': {len(matches)} matches")
                    for match in matches[:5]:  # Show first 5
                        print(f"    - {match}")
            
        except Exception as e:
            print(f"❌ Error testing {url}: {str(e)}")
    
    print(f"\n{'='*50}")
    print("💡 If you see dates being extracted correctly above,")
    print("   the issue might be in the event creation logic.")
    print("   If you see incorrect dates, the issue is in scraping.")

if __name__ == "__main__":
    test_subsplash_date_extraction()
