# Testing Setup Guide for Subsplash Calendar Bridge

This guide will help you test the sync functionality safely before running the actual sync to your live Google Calendars.

## 🚨 Important: This is a TEST environment

The test scripts will **NOT** modify your live Google Calendars. They only simulate what would happen during a real sync.

## 📋 Prerequisites

Before running tests, make sure you have:

1. **Python dependencies installed:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Google Calendar credentials:**
   - You need a `credentials.json` file for Google Calendar API access
   - This file should be in your project directory
   - If you don't have it, you'll need to set up Google Calendar API access

3. **Environment configuration:**
   - Copy `config.env.example` to `.env` if you haven't already
   - Update the calendar IDs in your `.env` file

## 🧪 Available Test Scripts

### 1. **Basic Functionality Test** (`test_sync_functionality.py`)
- Tests calendar configuration
- Tests Google Calendar authentication
- Tests event calendar mapping
- Tests date parsing functionality
- Tests basic Subsplash scraping

**Run with:**
```bash
python test_sync_functionality.py
```

### 2. **Dry Run Sync Test** (`test_dry_run_sync.py`)
- Simulates the complete sync process
- Shows exactly what events would be synced
- Analyzes dates and event data
- **NO actual changes to your calendars**

**Run with:**
```bash
# Test all calendars
python test_dry_run_sync.py

# Test specific calendar
python test_dry_run_sync.py bam
python test_dry_run_sync.py kids
python test_dry_run_sync.py prayer
```

### 3. **Test Runner** (`run_tests.py`)
- Interactive menu to run different tests
- Easy way to test specific aspects
- Run all tests in sequence

**Run with:**
```bash
python run_tests.py
```

## 🔍 What the Tests Will Show You

### ✅ **Calendar Configuration**
- Which calendars are enabled
- Subsplash URLs being scraped
- Google Calendar IDs being used

### ✅ **Event Data Quality**
- Number of events found
- Date range of events
- Event details (title, time, location, description)
- Date parsing accuracy

### ✅ **Sync Simulation**
- Which events would be created/updated
- Calendar mapping verification
- Data transformation accuracy

## 🚀 Testing Workflow

### Step 1: Basic Setup Test
```bash
python test_sync_functionality.py
```
This will verify your basic configuration and authentication.

### Step 2: Dry Run Sync
```bash
python test_dry_run_sync.py
```
This will show you exactly what would be synced without making changes.

### Step 3: Verify Results
Check that:
- ✅ All calendars are properly configured
- ✅ Events are being scraped correctly
- ✅ Dates are parsed accurately
- ✅ Events are mapped to correct calendars
- ✅ No duplicate or incorrect events

### Step 4: Run Live Sync (When Ready)
```bash
python sync_script.py
```
Only run this after all tests pass and you're confident in the results.

## 🎯 Testing Specific Calendars

If you want to test just one calendar:

```bash
# Test BAM calendar only
python test_dry_run_sync.py bam

# Test Kids calendar only
python test_dry_run_sync.py kids

# Test Prayer calendar only
python test_dry_run_sync.py prayer
```

## 🔧 Troubleshooting

### Authentication Issues
- Make sure `credentials.json` exists and is valid
- Check that your Google Calendar API is enabled
- Verify calendar IDs are correct

### Scraping Issues
- Check that Subsplash URLs are accessible
- Verify network connectivity
- Check for any rate limiting

### Date Parsing Issues
- Look for unusual date formats in the output
- Check if events have missing or malformed dates

## 📊 Expected Test Results

When tests pass successfully, you should see:

- ✅ All calendar configurations loaded
- ✅ Google Calendar authentication successful
- ✅ Events scraped from Subsplash
- ✅ Dates parsed correctly
- ✅ Events mapped to correct calendars
- ✅ No errors or warnings

## 🚨 When Tests Fail

If tests fail:

1. **Check the error messages** - they'll tell you what's wrong
2. **Verify your configuration** - check `.env` file and calendar IDs
3. **Check credentials** - ensure `credentials.json` is valid
4. **Review network access** - make sure Subsplash URLs are accessible
5. **Fix the issues** before running the live sync

## 💡 Pro Tips

- **Start with one calendar** - test `bam` first, then add others
- **Check the date range** - make sure events span the expected time period
- **Verify event details** - titles, times, and locations should make sense
- **Look for duplicates** - ensure the same event isn't being scraped multiple times

## 🎉 Ready to Sync?

Once all tests pass:

1. ✅ Configuration is correct
2. ✅ Authentication works
3. ✅ Events are scraped properly
4. ✅ Dates are parsed accurately
5. ✅ Calendar mapping is correct

Then you can safely run:
```bash
python sync_script.py
```

This will perform the actual sync to your Google Calendars.

---

**Remember: Always test first, sync second!** 🧪➡️🚀
