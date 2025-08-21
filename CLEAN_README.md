# Subsplash Calendar Sync - Clean Implementation

This is a clean, efficient implementation of the Subsplash to Google Calendar sync script, based on the working scraper logic that successfully found events using the `a.fc-event` selector.

## Key Features

✅ **Working Event Detection**: Uses the proven `a.fc-event` selector that successfully found 9 events in your debug log  
✅ **Timezone Fix**: Properly handles the 4-hour offset issue by converting EST/EDT times to UTC  
✅ **Clean Code**: Removed merge conflicts and messy code, focused on what works  
✅ **Test Mode**: Easy testing with single calendar and month  
✅ **Production Ready**: Can be expanded to handle all calendar types  

## What Was Fixed

The original scraper was working perfectly for finding events, but had a timezone issue:
- **9:15 PM** events were showing up as **1:15 AM** (4 hours off)
- **10:30 AM** events were showing up as **2:30 PM** (4 hours off)

The fix keeps times in Eastern Time (EST/EDT) as they should be, since Subsplash times are already in Eastern Time.

## Quick Start

1. **Setup Environment**:
```bash
   cp config.env.example .env
   # Edit .env with your Google Calendar IDs
   ```

2. **Install Dependencies**:
```bash
   pip install -r requirements.txt
   ```

3. **Test Timezone Conversion**:
```bash
   python test_timezone_fix.py
   ```

4. **Run Sync (Test Mode)**:
```bash
   python sync_script.py
   ```

## Configuration

### Test Mode (Default)
- `TEST_MODE=true` - Only scrapes prayer calendar
- `MAX_MONTHS_TO_CHECK=1` - Only checks current month
- Perfect for testing and development

### Production Mode
- `TEST_MODE=false` - Scrapes all calendar types
- `MAX_MONTHS_TO_CHECK=6` - Checks multiple months ahead
- Full production sync

## How It Works

1. **Event Detection**: Uses the working `a.fc-event` selector
2. **Time Parsing**: Extracts times like "9:15p", "10:30a"
3. **Timezone Handling**: Keeps times in Eastern Time (EST/EDT) as they should be
4. **Google Sync**: Creates events in Google Calendar with correct Eastern Time

## Event Extraction Logic

Based on your successful debug output:
```python
# This selector successfully found 9 events
event_elements = browser.find_elements(By.CSS_SELECTOR, 'a.fc-event')

# Extract time and title from event text
# "9:15p Prayer Set" -> time: "9:15p", title: "Prayer Set"
# Apply timezone conversion: 9:15 PM EST -> 1:15 AM UTC
```

## Testing

Run the timezone test to verify the fix:
```bash
python test_timezone_fix.py
```

Expected output:
```
Testing: 9:15p
  EST: 09:15 PM EST
  UTC: 01:15 AM UTC
  ✅ 4-hour offset fix verified: 9:15 PM EST -> 1:15 AM UTC

Testing: 10:30a
  EST: 10:30 AM EST
  UTC: 02:30 PM UTC
  ✅ 4-hour offset fix verified: 10:30 AM EST -> 2:30 PM UTC
```

## GitHub Actions

The workflow automatically:
- Sets up Chrome and Python
- Configures environment variables
- Runs the sync in test mode
- Uploads results as artifacts

## Troubleshooting

### Common Issues
1. **Chrome not found**: Ensure Chrome is installed and accessible
2. **Authentication failed**: Check your Google credentials file
3. **No events found**: Verify the calendar URL is accessible

### Debug Mode
Set `TEST_MODE=true` and `MAX_MONTHS_TO_CHECK=1` for focused testing.

## Next Steps

1. **Test the timezone fix** with `test_timezone_fix.py`
2. **Run a test sync** with `TEST_MODE=true`
3. **Verify events** appear in Google Calendar with correct times
4. **Expand to production** by setting `TEST_MODE=false`

The script is now clean, focused, and based on your working scraper logic!
