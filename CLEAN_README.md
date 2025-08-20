# Clean Subsplash Calendar Bridge

A streamlined, effective solution for automatically syncing events from your Subsplash calendar pages to Google Calendar using browser automation and GitHub Actions.

## 🎯 **What This Tool Does**

1. **Automated Scraping**: Uses real browser automation to navigate through your Subsplash calendar pages month by month
2. **Event Discovery**: Finds events by clicking through calendar navigation arrows (just like a human would)
3. **Google Calendar Sync**: Automatically creates/updates events in your Google Calendar
4. **Multi-Calendar Support**: Handles multiple ministry calendars (BAM, Kids, Prayer, etc.)
5. **Scheduled Operation**: Runs automatically every 6 hours via GitHub Actions

## 🚀 **Key Improvements Over Previous Version**

- **Real Browser Navigation**: Actually clicks calendar arrows to navigate months (not just URL manipulation)
- **Focused Scraping**: Single, effective strategy instead of trying 50+ different approaches
- **Cleaner Code**: Well-structured, maintainable Python code
- **Better Error Handling**: Graceful fallbacks and clear logging
- **Production Ready**: Optimized for GitHub Actions with minimal dependencies

## 📋 **Prerequisites**

1. **Google Calendar API credentials** (OAuth 2.0)
2. **GitHub repository** with Actions enabled
3. **Subsplash calendar URLs** for each ministry area
4. **Chrome browser** (automatically handled in GitHub Actions)

## 🛠️ **Setup Instructions**

### 1. **Clone and Configure**

```bash
git clone <your-repo>
cd SubsplashCalendarBridge
```

### 2. **Set up Google Calendar API**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Download the JSON credentials file
6. Share your Google Calendars with the OAuth client email

### 3. **Configure Environment Variables**

Copy `clean_config.env.example` to `.env` and fill in your calendar IDs:

```bash
cp clean_config.env.example .env
```

Edit `.env` with your actual calendar IDs:
```env
BAM_CALENDAR_ID=your_actual_bam_calendar_id
KIDS_CALENDAR_ID=your_actual_kids_calendar_id
PRAYER_CALENDAR_ID=your_actual_prayer_calendar_id
```

### 4. **Configure GitHub Secrets**

In your GitHub repository, go to **Settings > Secrets and variables > Actions** and add:

- `GOOGLE_CREDENTIALS`: The entire content of your OAuth credentials JSON file
- `GOOGLE_TOKEN`: Base64-encoded token.pickle file (generate this locally first)
- `BAM_CALENDAR_ID`: Your BAM Google Calendar ID
- `KIDS_CALENDAR_ID`: Your Kids Google Calendar ID  
- `PRAYER_CALENDAR_ID`: Your Prayer Google Calendar ID

### 5. **Generate OAuth Token (Local Setup)**

Before running in GitHub Actions, you need to generate a token locally:

```bash
# Install dependencies
pip install -r clean_requirements.txt

# Run the script locally (this will open a browser for OAuth)
python clean_sync_script.py
```

This will create a `token.pickle` file. Encode it for GitHub:

```bash
# On Windows
certutil -encode token.pickle token.pickle.b64

# On Mac/Linux
base64 -i token.pickle
```

Copy the encoded content to the `GOOGLE_TOKEN` secret in GitHub.

## 🔧 **Configuration Options**

### **Environment Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_MONTHS_TO_CHECK` | `6` | How many months ahead to scrape |
| `MAX_CONSECUTIVE_EMPTY_MONTHS` | `3` | Stop after this many empty months |
| `BROWSER_WAIT_TIME` | `10` | Seconds to wait after page loads |
| `LOG_LEVEL` | `info` | Logging level (info, warning, error) |

### **Calendar Configuration**

The script automatically handles these calendars:
- **BAM**: `https://antiochboone.com/calendar-bam`
- **Kingdom Kids**: `https://antiochboone.com/calendar-kids`
- **Prayer**: `https://antiochboone.com/calendar-prayer`

## 🚀 **How It Works**

### **1. Browser Automation**
- Opens Chrome browser (headless in production)
- Navigates to your Subsplash calendar page
- Waits for page to load completely

### **2. Month-by-Month Navigation**
- Extracts events from current month view
- Clicks the "next month" arrow/button
- Repeats until no more events found or limit reached

### **3. Event Extraction**
- Uses multiple CSS selectors to find event elements
- Parses event titles, dates, and times
- Falls back to text analysis if needed

### **4. Google Calendar Sync**
- Compares with existing events to avoid duplicates
- Creates new events or updates existing ones
- Handles both timed and all-day events

## 📊 **Expected Results**

- **Events synced every 6 hours** automatically
- **6+ months of future events** captured
- **No duplicate events** in Google Calendar
- **Clean, maintainable code** for future updates

## 🔍 **Troubleshooting**

### **Common Issues**

1. **"OAuth 2.0 interactive flow not supported in GitHub Actions"**
   - Solution: Generate token.pickle locally first, then encode for GitHub

2. **"No events found"**
   - Check: Subsplash URLs are correct and accessible
   - Check: Calendar pages actually contain events

3. **"Browser setup failed"**
   - Check: Chrome is available in GitHub Actions environment
   - Check: Dependencies are properly installed

### **Debug Mode**

For troubleshooting, you can enable debug options:

```env
SAVE_DEBUG_FILES=true
VERBOSE_DEBUG=true
SAVE_STATUS_FILE=true
LOG_LEVEL=debug
```

### **Local Testing**

Test the scraping locally before deploying:

```bash
# Test with debug enabled
export SAVE_DEBUG_FILES=true
export VERBOSE_DEBUG=true
python clean_sync_script.py
```

## 📁 **File Structure**

```
SubsplashCalendarBridge/
├── .github/workflows/
│   ├── clean_sync_calendar.yml     # New clean workflow
│   └── sync_calendar.yml           # Original workflow (keep for reference)
├── clean_sync_script.py            # New clean implementation
├── clean_requirements.txt          # Clean dependencies
├── clean_config.env.example        # Clean configuration template
├── CLEAN_README.md                 # This file
└── [original files...]             # Keep original for reference
```

## 🔄 **Migration from Old Version**

1. **Backup your current setup**
2. **Test the new implementation locally**
3. **Update GitHub secrets** with new format
4. **Switch to new workflow** by renaming files
5. **Monitor first few runs** to ensure success

## 🎉 **Success Indicators**

- **GitHub Actions**: Green checkmarks every 6 hours
- **Google Calendar**: New events appearing automatically
- **Future Events**: 6+ months of upcoming events visible
- **No Duplicates**: Clean event management
- **Reliable Operation**: Consistent, automated syncing

## 🤝 **Support & Maintenance**

### **Monitoring**
- Check GitHub Actions tab for workflow status
- Monitor Google Calendar for new events
- Review logs for any errors

### **Updates**
- The clean implementation is designed to be maintainable
- Easy to add new calendar types
- Simple to modify scraping logic

### **Scaling**
- Add new ministry calendars by updating the config
- Modify scraping parameters as needed
- Extend to other calendar platforms if desired

---

**Your Subsplash calendar will now automatically sync every 6 hours with real browser navigation!** 🎯

The new implementation focuses on what actually works: real browser automation that mimics human behavior, systematic month-by-month navigation, and clean, maintainable code.
