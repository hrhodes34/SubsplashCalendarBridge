#!/usr/bin/env python3
"""
Debug script to test event extraction logic step by step
"""

import os
import sys
from datetime import datetime
from bs4 import BeautifulSoup

def test_html_parsing():
    """Test parsing the actual HTML structure"""
    print("🔍 Testing HTML parsing...")
    
    # Read the debug HTML file
    html_file = "debug_page_source_prayer_20250820_170953.html"
    if not os.path.exists(html_file):
        print(f"❌ HTML file not found: {html_file}")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    print(f"✅ HTML parsed successfully")
    
    # Test 1: Find day cells
    print("\n📅 Test 1: Finding day cells...")
    day_cells = soup.find_all('td', class_='fc-daygrid-day')
    print(f"Found {len(day_cells)} day cells")
    
    # Show first few day cells
    for i, cell in enumerate(day_cells[:5]):
        data_date = cell.get('data-date')
        day_number = cell.find('a', class_='fc-daygrid-day-number')
        day_text = day_number.text.strip() if day_number else "NO_NUMBER"
        print(f"  Cell {i}: data-date='{data_date}' day='{day_text}'")
    
    # Test 2: Find events
    print("\n🎯 Test 2: Finding events...")
    events = soup.find_all('a', class_='fc-event')
    print(f"Found {len(events)} events")
    
    # Show first few events
    for i, event in enumerate(events[:5]):
        # Get time
        time_elem = event.find('div', class_='fc-event-time')
        time_text = time_elem.text.strip() if time_elem else "NO_TIME"
        
        # Get title
        title_elem = event.find('div', class_='fc-event-title')
        title_text = title_elem.text.strip() if title_elem else "NO_TITLE"
        
        # Get href
        href = event.get('href', 'NO_HREF')
        
        print(f"  Event {i}: time='{time_text}' title='{title_text}' href='{href}'")
        
        # Find the parent day cell
        parent_cell = event.find_parent('td', class_='fc-daygrid-day')
        if parent_cell:
            cell_date = parent_cell.get('data-date')
            print(f"    Parent cell date: {cell_date}")
        else:
            print(f"    No parent cell found")
    
    # Test 3: Test the XPath-like logic
    print("\n🔗 Test 3: Testing parent cell finding...")
    for i, event in enumerate(events[:3]):
        print(f"\n  Event {i}: {event.find('div', class_='fc-event-title').text.strip()}")
        
        # Method 1: Direct parent
        parent_cell = event.find_parent('td', class_='fc-daygrid-day')
        if parent_cell:
            data_date = parent_cell.get('data-date')
            print(f"    Method 1 (find_parent): {data_date}")
        else:
            print(f"    Method 1: No parent found")
        
        # Method 2: Look for ancestor with data-date
        ancestor_with_date = event.find_parent(attrs={'data-date': True})
        if ancestor_with_date:
            data_date = ancestor_with_date.get('data-date')
            print(f"    Method 2 (ancestor with data-date): {data_date}")
        else:
            print(f"    Method 2: No ancestor with data-date found")
        
        # Method 3: Look for any parent with data-date
        all_parents = event.find_parents()
        date_found = False
        for parent in all_parents:
            if parent.get('data-date'):
                data_date = parent.get('data-date')
                print(f"    Method 3 (any parent): {data_date}")
                date_found = True
                break
        if not date_found:
            print(f"    Method 3: No parent with data-date found")

if __name__ == "__main__":
    test_html_parsing()
