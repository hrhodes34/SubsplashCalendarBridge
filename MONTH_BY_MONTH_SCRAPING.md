# Month-by-Month Calendar Scraping Strategy

## 🎯 **Problem Solved**
Your original scraping was only capturing events 2-3 weeks out, but you have events loaded for months ahead of time. This new approach systematically scrapes the church's calendar month by month until it finds completely empty months.

## 🚀 **New Month-by-Month Approach**

### **1. Systematic Month Navigation**
Instead of trying to get all events at once, the script now:
- **Starts from the current month** and systematically moves forward
- **Tries multiple URL patterns** for each month (e.g., `?month=12&year=2024`, `?date=2024-12`)
- **Continues until it finds 3 consecutive empty months** (configurable)
- **Has a safety limit** of 60 months (5 years) to prevent infinite loops

### **2. Multiple URL Patterns Per Month**
For each month, the script tries these URL variations:
```
https://antiochboone.com/calendar?month=12&year=2024
https://antiochboone.com/calendar?m=12&y=2024
https://antiochboone.com/calendar/2024/12
https://antiochboone.com/calendar/month/2024/12
https://antiochboone.com/calendar/calendar/2024/12
https://antiochboone.com/calendar?date=2024-12
https://antiochboone.com/calendar?view=month&month=12&year=2024
```

### **3. Alternative Calendar Sources**
The script also tries these alternative calendar URLs:
- `https://antiochboone.com/events`
- `https://antiochboone.com/calendar/events`
- `https://antiochboone.com/upcoming-events`
- `https://antiochboone.com/all-events`
- `https://subsplash.com/+wrmm/lb/ca/+pysr4r6/events`

### **4. Feed Discovery**
The script looks for calendar feeds in various formats:
- **JSON feeds**: `/calendar.json`, `/events.json`
- **XML/RSS feeds**: `/calendar/rss`, `/events/rss`
- **iCal feeds**: `/calendar.ics`, `/events.ics`

## 🔍 **How It Works**

### **Step 1: Month-by-Month Scraping**
```
🗓️ Starting systematic calendar scraping from December 2024
🔍 Checking December 2024...
  ✅ Found 15 events via /calendar
  📅 Total events for December 2024: 15
🔍 Checking January 2025...
  ✅ Found 12 events via /calendar
  📅 Total events for January 2025: 12
🔍 Checking February 2025...
  ✅ Found 8 events via /calendar
  📅 Total events for February 2025: 8
🔍 Checking March 2025...
  📭 Month March 2025 is empty (consecutive empty: 1)
🔍 Checking April 2025...
  📭 Month April 2025 is empty (consecutive empty: 2)
🔍 Checking May 2025...
  📭 Month May 2025 is empty (consecutive empty: 3)
🛑 Stopping after 3 consecutive empty months
```

### **Step 2: Alternative Source Discovery**
```
🔍 Trying alternative calendar navigation approaches...
  🔍 Trying alternative calendar URLs...
    ✅ events: Found 45 events
    ✅ calendar/events: Found 38 events
    ⚠️ upcoming-events: No events found
    ✅ all-events: Found 52 events
```

### **Step 3: Feed Discovery**
```
🔍 Looking for embedded calendar data...
  ✅ Found 23 events in JSON feed: events.json
  ✅ Found 18 events in iCal feed: calendar.ics
```

## 📊 **Expected Results**

With this approach, you should now see:
- **Events extending 6-18 months into the future** (instead of 2-3 weeks)
- **Much higher event counts** as events are found from multiple sources
- **Better coverage** of recurring events and future planning
- **More accurate event dates** from structured feeds

## 🧪 **Testing the New Approach**

Run the test script to see the enhanced scraping in action:
```bash
python test_scraping.py
```

The output will show:
- Month-by-month scraping progress
- Alternative source discovery
- Feed parsing results
- Event distribution by month
- Total events found from all sources

## ⚙️ **Configuration Options**

You can adjust these parameters in the code:
- **`max_consecutive_empty = 3`**: Stop after this many empty months
- **`max_months_to_check = 60`**: Maximum months to check (safety limit)
- **`time.sleep(1)`**: Delay between month requests (be respectful to server)

## 🔧 **Troubleshooting**

### **If Still Not Getting Future Events**
1. **Check the church's calendar page** manually to see how months are navigated
2. **Look for "Next Month" buttons** or date pickers
3. **Check if there are different calendar views** (month, year, list)
4. **Look for RSS/JSON feeds** in the page source

### **If Getting Rate Limited**
1. **Increase delays** between requests (`time.sleep(2)` or higher)
2. **Reduce the number of URL patterns** tried per month
3. **Focus on the most successful URL patterns** first

## 🎉 **Benefits of This Approach**

1. **Comprehensive Coverage**: Goes month by month until no more events
2. **Multiple Sources**: Combines direct scraping with feed discovery
3. **Future-Proof**: Will automatically find events as they're added
4. **Respectful**: Includes delays and stops when no more content
5. **Debugging**: Shows exactly what's happening each month

This approach should finally capture all those future events you mentioned!
