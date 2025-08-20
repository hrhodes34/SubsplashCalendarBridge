#!/usr/bin/env python3
"""
Diagnostic script to understand what's happening with the Subsplash calendar
"""

import requests
from bs4 import BeautifulSoup
import json

def diagnose_calendar(url):
    """Diagnose what type of calendar we're dealing with"""
    print(f"🔍 Diagnosing calendar: {url}")
    print("=" * 80)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Content Length: {len(response.content)} bytes")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for FullCalendar
        fc_elements = soup.find_all(class_=lambda x: x and 'fc-' in str(x))
        print(f"\n📅 FullCalendar elements found: {len(fc_elements)}")
        
        # Look for JavaScript calendar loading
        scripts = soup.find_all('script')
        calendar_scripts = []
        for script in scripts:
            if script.string and any(keyword in script.string.lower() for keyword in ['calendar', 'event', 'fullcalendar']):
                calendar_scripts.append(script.string[:200] + '...' if len(script.string) > 200 else script.string)
        
        print(f"📜 JavaScript with calendar keywords: {len(calendar_scripts)}")
        for i, script in enumerate(calendar_scripts[:3]):  # Show first 3
            print(f"   Script {i+1}: {script}")
        
        # Look for AJAX/API endpoints
        api_keywords = ['api', 'ajax', 'events', 'calendar.json', 'feed']
        api_references = []
        for script in scripts:
            if script.string:
                for keyword in api_keywords:
                    if keyword in script.string.lower():
                        api_references.append(f"Found '{keyword}' in script")
                        break
        
        print(f"\n🔗 Potential API references: {len(api_references)}")
        for ref in api_references[:5]:
            print(f"   • {ref}")
        
        # Look for embed/iframe content
        iframes = soup.find_all('iframe')
        print(f"\n🖼️  IFrames found: {len(iframes)}")
        for iframe in iframes:
            src = iframe.get('src', 'No src')
            print(f"   • {src}")
        
        # Look for data attributes that might contain events
        data_elements = soup.find_all(attrs=lambda x: x and isinstance(x, dict) and any(k.startswith('data-') for k in x.keys()))
        calendar_data = []
        for elem in data_elements:
            if hasattr(elem, 'attrs') and elem.attrs:
                for attr, value in elem.attrs.items():
                    if attr.startswith('data-') and any(keyword in attr.lower() for keyword in ['event', 'calendar', 'date']):
                        calendar_data.append(f"{attr}: {str(value)[:100]}")
        
        print(f"\n📊 Data attributes with calendar/event keywords: {len(calendar_data)}")
        for data in calendar_data[:5]:
            print(f"   • {data}")
        
        # Check if it's using a common calendar service
        calendar_services = ['subsplash', 'churchcenter', 'eventbrite', 'google calendar', 'outlook']
        found_services = []
        content_text = response.text.lower()
        for service in calendar_services:
            if service in content_text:
                found_services.append(service)
        
        print(f"\n🏢 Calendar services detected: {found_services}")
        
        # Look for potential event data in JSON
        json_patterns = []
        import re
        json_matches = re.findall(r'\{[^}]*"(?:event|calendar|date|title)"[^}]*\}', response.text, re.IGNORECASE)
        print(f"\n📋 Potential JSON event data: {len(json_matches)}")
        for match in json_matches[:3]:
            print(f"   • {match[:100]}...")
        
        # Summary and recommendations
        print(f"\n" + "=" * 80)
        print("📋 DIAGNOSIS SUMMARY:")
        print("=" * 80)
        
        if len(fc_elements) > 0:
            print("✅ This appears to be a FullCalendar implementation")
            print("💡 Recommendation: Use browser automation (Selenium) to load the page and extract events")
        elif len(iframes) > 0:
            print("✅ This appears to use embedded calendar content")
            print("💡 Recommendation: Check iframe sources for direct event data")
        elif len(calendar_scripts) > 0:
            print("✅ This appears to use JavaScript to load calendar data")
            print("💡 Recommendation: Use browser automation or find the AJAX endpoint")
        else:
            print("❌ No clear calendar implementation detected")
            print("💡 Recommendation: Manual inspection needed")
        
        # Show sample of what's actually being extracted
        print(f"\n📄 SAMPLE OF CURRENT EXTRACTION:")
        print("-" * 40)
        all_text = soup.get_text()
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        for i, line in enumerate(lines[:20]):  # Show first 20 lines
            print(f"   {i+1:2d}. {line[:80]}...")
        
    except Exception as e:
        print(f"❌ Error diagnosing calendar: {str(e)}")

def main():
    urls = [
        "https://antiochboone.com/calendar-prayer",
        "https://antiochboone.com/calendar-bam", 
        "https://antiochboone.com/calendar-kids"
    ]
    
    for url in urls:
        diagnose_calendar(url)
        print("\n" + "="*100 + "\n")

if __name__ == "__main__":
    main()
