# Subsplash Calendar Bridge - Scraping Improvements

## Overview
This document outlines the significant improvements made to the Subsplash calendar scraping functionality to make it much more thorough and capture more events.

## Key Improvements Made

### 1. **Multiple URL Variations**
The script now tries multiple URL variations to find more events:
- Original embed URL
- Different view modes (calendar, list, month, year)
- Different limits (100, 200 events)
- Include past/future events flags
- Show all events flag

### 2. **Enhanced CSS Selector Strategy**
Instead of relying on a single CSS selector, the script now tries multiple selectors:
- `div.kit-list-item__text` (original)
- `div.kit-list-item`
- `div[class*="list-item"]`
- `div[class*="event"]`
- `div[class*="calendar"]`
- `article`, `li`, and other common containers
- `div[class*="kit"]`, `div[class*="item"]`, etc.

### 3. **Fallback Event Extraction**
When standard selectors fail, the script uses multiple fallback methods:
- **JSON Data Extraction**: Searches script tags for JSON event data
- **Text Pattern Analysis**: Uses regex patterns to find events in page text
- **Meta Tag Analysis**: Extracts event information from meta tags and data attributes

### 4. **Improved Date/Time Parsing**
Enhanced datetime parsing to handle more formats:
- Single day events: "August 20, 2025 from 6:00 - 8:00pm EDT"
- Multi-day events: "August 22, 6:00pm - August 24, 2025 11:00am EDT"
- Alternative formats with different time patterns
- Simple date formats for all-day events
- Fallback pattern matching for any date/time combination

### 5. **Pagination Handling**
Automatically detects and handles pagination:
- Tries different pagination patterns (`&page=`, `&offset=`, `&start=`)
- Attempts up to 5 pages to find more events
- Stops when no more events are found

### 6. **API Endpoint Discovery**
Attempts to find and call potential API endpoints:
- Common Subsplash API patterns
- JSON endpoints for events and calendar data
- Automatic parsing of API responses

### 7. **Enhanced Debugging and Analysis**
Comprehensive debugging features:
- Saves HTML content for analysis
- Analyzes page structure and CSS classes
- Shows potential event titles and date patterns
- Detailed logging of what's found and what's not

### 8. **Duplicate Prevention**
Smart deduplication based on:
- Event title
- Start time
- Prevents duplicate events from multiple sources

## How It Works

1. **Primary Scraping**: Tries multiple URL variations with enhanced selectors
2. **Fallback Methods**: If few events found, uses JSON/text/meta extraction
3. **Pagination**: Automatically handles multi-page calendars
4. **API Discovery**: Tries to find direct API endpoints
5. **Deduplication**: Removes duplicate events from all sources
6. **Debug Output**: Provides detailed information about what was found

## Testing

Use the `test_scraping.py` script to test the improved functionality:

```bash
python test_scraping.py
```

This will test the scraping without requiring Google Calendar authentication.

## Expected Results

The improved scraping should now capture:
- **More events**: From multiple sources and formats
- **Longer time ranges**: Events beyond just a couple weeks
- **Different event types**: Various event formats and structures
- **Better reliability**: Multiple fallback methods ensure events are found

## Troubleshooting

If you're still not getting all events:

1. **Check the debug output**: Look for the HTML analysis and selector results
2. **Review saved HTML**: Check `subsplash_page.html` for the actual page content
3. **Try different URLs**: The script will show which URL variations work
4. **Check for JavaScript**: Some events might be loaded dynamically

## Dependencies

Make sure you have all required packages:
```bash
pip install -r requirements.txt
```

## Next Steps

If you need even more thorough scraping, consider:
1. **Selenium**: For JavaScript-heavy pages
2. **API Documentation**: Check if Subsplash provides official API access
3. **Rate Limiting**: Add delays between requests if needed
4. **User Authentication**: Some calendars might require login

The improved scraping should significantly increase the number of events captured from your Subsplash calendar!
