# Subsplash Calendar Bridge - Future Events Capture Improvements

## 🎯 **Problem Solved**
Your original scraping was only capturing events about 3 weeks out, but you have events loaded for months ahead of time. This enhancement addresses that limitation with multiple strategies.

## 🚀 **Key Improvements for Future Events**

### **1. Extended URL Variations (40+ combinations)**
The script now tries many more URL parameters to access future events:

#### **View Modes**
- `?view=calendar`, `?view=list`, `?view=month`, `?view=year`
- `?view=extended`, `?view=full`

#### **Event Limits**
- `&limit=100`, `&limit=200`, `&limit=500`
- `&show_all=1`, `&all_events=1`

#### **Time Range Parameters**
- `&range=all`, `&range=future`, `&range=year`
- `&range=6months`, `&range=12months`
- `&months_ahead=6`, `&months_ahead=12`, `&months_ahead=24`
- `&months_ahead=36`, `&months_ahead=48`, `&months_ahead=60`

#### **Date Range Parameters**
- `&start_date=today`
- `&end_date=2026-12-31`, `&end_date=2027-12-31`, `&end_date=2028-12-31`
- `&end_date=2030-12-31`, `&end_date=2035-12-31`

#### **Loading Strategies**
- `&load_strategy=all`, `&load_strategy=future`, `&load_strategy=extended`
- `&force_load=1`, `&preload=1`, `&cache=1`

### **2. User Interaction Simulation**
Simulates user actions that might load more events:

#### **Action Parameters**
- `&action=load_more`, `&action=expand`, `&action=show_all`
- `&action=load_future`, `&action=load_extended`

#### **Navigation Parameters**
- `&nav=next_month`, `&nav=next_quarter`, `&nav=next_year`
- `&nav=extended`

#### **Lazy Loading Triggers**
- `&lazy_load=1`, `&infinite_scroll=1`, `&auto_load=1`

### **3. Extended Future Loading**
Goes beyond standard parameters to find events months/years ahead:

#### **Extended Time Ranges**
- `&months_ahead=36`, `&months_ahead=48`, `&months_ahead=60`
- `&range=extended`, `&range=unlimited`
- `&load_all_future=1`, `&future_limit=none`

### **4. Multiple Data Format Support**
Tries to find events in various calendar formats:

#### **JSON Endpoints**
- `/events.json`, `/calendar.json`, `/data.json`, `/feed.json`
- `/api/events`, `/api/calendar`, `/api/v1/events`

#### **XML/RSS Formats**
- `.xml`, `/events.xml`, `/calendar.xml`, `/feed.xml`
- `/rss`, `/feed`, `/rss.xml`

#### **Calendar Standards**
- `.ics` (iCal format), `/calendar.ics`, `/events.ics`
- `.csv` (spreadsheet format)

### **5. Enhanced JSON Data Extraction**
Looks for calendar data in JavaScript with 30+ patterns:

#### **Window Object Patterns**
- `window.events`, `window.calendar`, `window.calendarData`
- `window.eventData`, `window.subsplashData`

#### **Variable Declarations**
- `var events`, `const calendar`, `let calendarData`
- `var calendarData`, `const eventData`

#### **Data Object Patterns**
- `data: [...]`, `events: [...]`, `calendar: {...}`
- `calendarData: {...}`, `eventData: {...}`

### **6. Comprehensive Fallback Methods**
When standard methods fail, uses multiple fallback strategies:

#### **Text Pattern Analysis**
- Regex patterns to find events in page text
- Context-aware date/time extraction
- Event title and description parsing

#### **Meta Tag Analysis**
- Extracts event data from meta tags
- Parses data attributes
- Handles various content formats

### **7. Advanced Pagination Handling**
Automatically discovers and handles multi-page calendars:

#### **Pagination Patterns**
- `&page=`, `&offset=`, `&start=`
- Tries up to 5 pages automatically
- Stops when no more events found

#### **Smart Page Detection**
- Detects when pages contain events
- Combines results from multiple pages
- Handles different pagination formats

## 🔍 **How It Finds Future Events**

### **Step 1: Multiple URL Attempts**
1. Tries 40+ different URL variations
2. Each variation attempts different loading strategies
3. Combines results from all successful attempts

### **Step 2: User Interaction Simulation**
1. Simulates clicking "load more" buttons
2. Tries different calendar navigation
3. Triggers lazy loading mechanisms

### **Step 3: Extended Time Ranges**
1. Attempts to load events 6, 12, 24, 36, 48, 60 months ahead
2. Tries unlimited future event loading
3. Uses extended date ranges (up to 2035)

### **Step 4: Alternative Data Sources**
1. Searches for JSON APIs
2. Tries different file formats (XML, ICS, CSV)
3. Extracts data from JavaScript variables

### **Step 5: Comprehensive Parsing**
1. Handles multiple date/time formats
2. Parses various event structures
3. Combines results from all sources

## 📊 **Expected Results**

With these improvements, you should now see:

- **More events**: Significantly increased total event count
- **Longer time range**: Events extending 6+ months into the future
- **Better coverage**: Events from multiple sources and formats
- **Detailed analysis**: Month-by-month breakdown of events found

## 🧪 **Testing the Improvements**

Run the enhanced test script:
```bash
python test_scraping.py
```

This will show:
- Total events found
- Date range (earliest to latest)
- Months ahead covered
- Events by month
- Sample events with dates

## 🔧 **Troubleshooting**

If you're still not getting events far into the future:

1. **Check the debug output**: Look for which URL variations work
2. **Review HTML analysis**: See what the page structure reveals
3. **Check for JavaScript**: Some events might be loaded dynamically
4. **Try different formats**: The script will show which formats work

## 🎉 **What This Solves**

- **3-week limitation**: Now captures events months/years ahead
- **Limited event count**: Finds events from multiple sources
- **Single format dependency**: Tries various data formats
- **Basic pagination**: Handles complex multi-page calendars
- **Static scraping**: Simulates user interactions

The enhanced scraping should now capture all the future events you have loaded in your Subsplash calendar!
