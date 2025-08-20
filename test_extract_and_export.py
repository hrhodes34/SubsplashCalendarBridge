#!/usr/bin/env python3
"""
Test script to extract Subsplash events and export to CSV for analysis
"""

import os
import sys
import csv
import json
from datetime import datetime
from sync_script import SubsplashSyncService, get_enabled_calendars

def export_events_to_csv(calendar_key=None):
    """Extract events and export to CSV for analysis"""
    print("🧪 Starting Event Extraction and CSV Export...")
    print("=" * 80)
    
    enabled_calendars = get_enabled_calendars()
    if not enabled_calendars:
        print("❌ No enabled calendars found!")
        return False
    
    if calendar_key and calendar_key in enabled_calendars:
        calendars_to_test = {calendar_key: enabled_calendars[calendar_key]}
    else:
        calendars_to_test = enabled_calendars
    
    all_results = []
    
    for cal_key, cal_config in calendars_to_test.items():
        print(f"\n{'='*60}")
        print(f"🔄 EXTRACTING: {cal_config['name']}")
        print(f"{'='*60}")
        
        try:
            # Create service
            service = SubsplashSyncService(cal_config)
            
            # Scrape events (don't require authentication for this test)
            print("🌐 Scraping Subsplash events...")
            events = service.scrape_subsplash_events()
            
            if not events:
                print("❌ No events found from Subsplash")
                continue
            
            print(f"✅ Found {len(events)} events from Subsplash")
            
            # Process each event for CSV export
            for i, event in enumerate(events):
                result = {
                    'calendar': cal_config['name'],
                    'calendar_key': cal_key,
                    'event_index': i + 1,
                    'title': event.get('title', 'No Title'),
                    'date': event.get('date', 'No Date'),
                    'time': event.get('time', 'No Time'),
                    'start_datetime': event.get('start_datetime', 'No Start DateTime'),
                    'end_datetime': event.get('end_datetime', 'No End DateTime'),
                    'raw_text': str(event.get('raw_text', 'No Raw Text'))[:200],  # Limit length
                    'location': event.get('location', 'No Location'),
                    'description': str(event.get('description', 'No Description'))[:200],  # Limit length
                    'all_day': event.get('all_day', False),
                    'event_data': json.dumps(event, default=str)[:500]  # Limit length
                }
                all_results.append(result)
                
                # Print sample events
                if i < 5:  # Show first 5 events
                    print(f"  📅 Event {i+1}: {result['title']}")
                    print(f"      Date: {result['date']}")
                    print(f"      Time: {result['time']}")
                    print(f"      Raw: {result['raw_text'][:100]}...")
                    
        except Exception as e:
            print(f"💥 Error extracting {cal_config['name']}: {str(e)}")
            continue
    
    if not all_results:
        print("❌ No events extracted from any calendar")
        return False
    
    # Export to CSV
    csv_filename = f"extracted_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'calendar', 'calendar_key', 'event_index', 'title', 'date', 'time',
                'start_datetime', 'end_datetime', 'raw_text', 'location', 
                'description', 'all_day', 'event_data'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in all_results:
                writer.writerow(result)
        
        print(f"\n✅ Exported {len(all_results)} events to: {csv_filename}")
        print(f"📊 Summary by calendar:")
        
        # Show summary
        calendar_counts = {}
        for result in all_results:
            cal = result['calendar']
            if cal not in calendar_counts:
                calendar_counts[cal] = 0
            calendar_counts[cal] += 1
        
        for cal, count in calendar_counts.items():
            print(f"   • {cal}: {count} events")
        
        print(f"\n💡 Open {csv_filename} in Excel or Google Sheets to analyze the data")
        print("   Look specifically at the 'raw_text' and 'event_data' columns to see what's being parsed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error exporting to CSV: {str(e)}")
        return False

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Extract and export Subsplash events to CSV')
    parser.add_argument('--calendar', choices=['bam', 'kids', 'prayer'], 
                       help='Specific calendar to test (default: all)')
    
    args = parser.parse_args()
    
    success = export_events_to_csv(args.calendar)
    if success:
        print("\n🎉 Export completed successfully!")
    else:
        print("\n💥 Export failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
