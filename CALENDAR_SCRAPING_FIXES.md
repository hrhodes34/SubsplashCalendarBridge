# Calendar Scraping Fixes

## Issues Identified and Fixed

### 1. **Time Extraction Problem**
**Issue**: The scraper was not correctly extracting event times from FullCalendar events.

**Root Cause**: The original code was trying to parse time from the combined text content, but FullCalendar stores time in a separate `<div class="fc-event-time">` element.

**HTML Structure**:
```html
<a class="fc-event">
    <div class="fc-event-main">
        <div class="fc-event-main-frame">
            <div class="fc-event-time">5:15p</div>  <!-- Time is here -->
            <div class="fc-event-title-container">
                <div class="fc-event-title">Prayer Set</div>  <!-- Title is here -->
            </div>
        </div>
    </div>
</a>
```

**Fix Applied**: Modified `_extract_fc_event()` method to:
- First look for `.fc-event-time` element to extract time
- Then look for `.fc-event-title` element to extract title
- Fall back to text parsing if elements not found

### 2. **Weekly Event Detection Problem**
**Issue**: Weekly recurring events were only being displayed once per month instead of weekly.

**Root Cause**: The scraper was finding individual event instances but not recognizing the weekly pattern or expanding them.

**Fix Applied**: Enhanced `_detect_weekly_recurring_events()` method to:
- Group events by title to detect patterns
- Use known weekly patterns for key events:
  - **Early Morning Prayer**: 6:30 AM on weekdays (Mon-Fri)
  - **Prayer Set**: 5:15 PM on weekdays (Mon-Fri)  
  - **BAM**: 7:15 AM on weekdays (Mon-Fri)
- Expand weekly events for the next 3 months (12 weeks)
- Preserve original scraped events while adding recurring instances

### 3. **Date Extraction Problem**
**Issue**: Events were being assigned incorrect dates (often the first day of the month).

**Root Cause**: The scraper was not properly navigating the FullCalendar DOM structure to find the actual event dates.

**Fix Applied**: Improved date extraction logic in `_extract_fc_event()` method to:
- Look for `data-date` attribute in parent day cells
- Navigate up the DOM tree to find date information
- Use proper FullCalendar selectors (`.fc-daygrid-day`, `data-date`)
- Added better logging for debugging date extraction

## Expected Results After Fixes

### Before Fixes:
```json
{
  "title": "6:30a\nEarly Morning Prayer",
  "start": "2025-08-01 00:00:00",
  "end": "2025-08-01 23:59:00",
  "time": "All day",
  "all_day": true
}
```

### After Fixes:
```json
{
  "title": "Early Morning Prayer",
  "start": "2025-09-04 06:30:00",
  "end": "2025-09-04 07:30:00",
  "time": "6:30a",
  "all_day": false,
  "recurring": true,
  "pattern": "Weekly on Monday, Tuesday, Wednesday, Thursday, Friday"
}
```

## Weekly Event Expansion

The system now automatically creates weekly recurring events:

- **Early Morning Prayer**: Every weekday at 6:30 AM
- **Prayer Set**: Every weekday at 5:15 PM  
- **BAM**: Every weekday at 7:15 AM

Each event is expanded for 12 weeks (3 months) into the future, so instead of seeing just one instance per month, you'll see:
- Week 1: Monday, Tuesday, Wednesday, Thursday, Friday
- Week 2: Monday, Tuesday, Wednesday, Thursday, Friday
- Week 3: Monday, Tuesday, Wednesday, Thursday, Friday
- ... and so on for 12 weeks

## Testing the Fixes

### 1. Test Time Parsing:
```bash
python test_time_parsing.py
```

### 2. Test Full Scraping:
```bash
python test_improved_scraping.py
```

### 3. Test Production Sync:
```bash
python sync_script.py
```

## Key Changes Made

1. **`_extract_fc_event()` method**: Fixed time and title extraction from FullCalendar DOM
2. **`_detect_weekly_recurring_events()` method**: Enhanced weekly pattern detection and expansion
3. **Date extraction logic**: Improved navigation of FullCalendar structure
4. **Logging**: Added better debugging information for troubleshooting

## GitHub Actions Considerations

Since this runs in GitHub Actions (headless environment):
- Browser setup uses `--headless` mode
- No visual rendering, so DOM structure must be fully loaded
- Added proper wait times for FullCalendar to render events
- Enhanced error handling for headless environment

## Next Steps

1. **Test the fixes** with the provided test scripts
2. **Run a full sync** to verify weekly events are properly expanded
3. **Monitor the logs** to ensure time and date extraction is working
4. **Verify Google Calendar sync** shows weekly recurring events correctly

The fixes should resolve both the time parsing issues and the weekly event display problems, giving you properly formatted weekly recurring events with correct times.
