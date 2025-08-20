# Subsplash Calendar Bridge

Automatically sync events from your Subsplash calendar to Google Calendar using GitHub Actions.

## 🚀 **Features**

- **Automated syncing** every 6 hours via GitHub Actions
- **Comprehensive event discovery** with multiple scraping strategies
- **Future event capture** extending months/years ahead
- **Production-ready** with no unnecessary file modifications
- **Debug mode** available when troubleshooting is needed

## 📋 **Prerequisites**

1. **Google Calendar API credentials** (Service Account)
2. **GitHub repository** with Actions enabled
3. **Subsplash calendar URL** (your church's calendar)

## 🛠️ **Setup**

### 1. **Clone and Configure**

```bash
git clone <your-repo>
cd SubsplashCalendarBridge
```

### 2. **Set up Google Calendar API**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create a Service Account
5. Download the JSON credentials file
6. Share your Google Calendar with the service account email

### 3. **Configure GitHub Secrets**

In your GitHub repository, go to **Settings > Secrets and variables > Actions** and add:

- `GOOGLE_CREDENTIALS`: The entire content of your credentials.json file
- `GOOGLE_CALENDAR_ID`: Your Google Calendar ID (found in calendar settings)
- `SUBSPLASH_EMBED_URL`: Your Subsplash calendar URL

### 4. **Install Dependencies**

```bash
pip install -r requirements.txt
```

## 🔧 **Configuration**

### **Environment Variables**

The system uses environment variables to control behavior:

| Variable | Default | Description |
|----------|---------|-------------|
| `SAVE_DEBUG_FILES` | `false` | Save HTML debug files |
| `VERBOSE_DEBUG` | `false` | Enable detailed page analysis |
| `SAVE_STATUS_FILE` | `false` | Save sync status files |
| `LOG_LEVEL` | `info` | Logging level (info, warning, error) |

### **Production vs Development**

- **Production**: All debug options disabled by default
- **Development**: Enable debug options when troubleshooting

## 🚀 **Usage**

### **Automated Sync (Production)**

The main workflow runs automatically every 6 hours:

1. **No file modifications** - Clean, production-ready operation
2. **Automatic error handling** - Fails gracefully if issues occur
3. **Efficient operation** - Only syncs what's needed

### **Manual Debug Runs**

When you need to troubleshoot:

1. Go to **Actions** tab in your GitHub repo
2. Select **Sync Calendar (Debug Mode)**
3. Click **Run workflow**
4. Debug files are uploaded as artifacts (7-day retention)

### **Local Testing**

```bash
# Test scraping without Google Calendar sync
python test_scraping.py

# Test full sync (requires credentials.json)
python sync_script.py
```

## 📊 **What Gets Synced**

The enhanced scraping captures:

- **More events** from multiple sources and formats
- **Longer time ranges** extending 6+ months into the future
- **Better coverage** using multiple scraping strategies
- **Various event types** with comprehensive parsing

## 🔍 **Troubleshooting**

### **Enable Debug Mode**

Set environment variables to `true`:

```bash
export SAVE_DEBUG_FILES=true
export VERBOSE_DEBUG=true
export SAVE_STATUS_FILE=true
```

### **Check Logs**

The system provides detailed logging:
- Page structure analysis
- Event discovery results
- Sync status and errors

### **Common Issues**

1. **Authentication errors**: Check Google Calendar sharing
2. **No events found**: Verify Subsplash URL is correct
3. **Rate limiting**: System includes automatic delays

## 📁 **File Structure**

```
SubsplashCalendarBridge/
├── .github/workflows/
│   ├── sync_calendar.yml          # Production workflow
│   └── sync_calendar_debug.yml    # Debug workflow
├── sync_script.py                 # Main sync script
├── test_scraping.py               # Testing script
├── requirements.txt                # Python dependencies
├── config.env.example             # Configuration template
└── README.md                      # This file
```

## 🔄 **Workflow Details**

### **Production Workflow**
- **Schedule**: Every 6 hours
- **Debug files**: Disabled
- **Status files**: Disabled
- **Clean operation**: No file modifications

### **Debug Workflow**
- **Trigger**: Manual only
- **Debug files**: Enabled
- **Status files**: Enabled
- **Artifacts**: Debug files uploaded for 7 days

## 🎯 **Best Practices**

1. **Use production workflow** for regular syncing
2. **Use debug workflow** only when troubleshooting
3. **Monitor Actions tab** for sync status
4. **Check logs** if events aren't syncing
5. **Keep credentials secure** in GitHub secrets

## 🚨 **Security Notes**

- **Never commit** credentials.json to your repository
- **Use GitHub secrets** for sensitive information
- **Service account** has minimal required permissions
- **Debug files** are temporary and automatically cleaned up

## 📈 **Monitoring**

### **GitHub Actions**
- Check **Actions** tab for workflow status
- View logs for detailed execution information
- Monitor for failed runs

### **Google Calendar**
- Verify events are being created/updated
- Check sync frequency and timing
- Monitor for duplicate events

## 🤝 **Support**

If you encounter issues:

1. **Check the logs** in GitHub Actions
2. **Enable debug mode** to get more information
3. **Verify configuration** (secrets, calendar sharing)
4. **Test locally** with test_scraping.py

## 🎉 **Success Indicators**

- **Events syncing** every 6 hours
- **No file modifications** in repository
- **Clean workflow runs** with green checkmarks
- **Events appearing** in Google Calendar
- **Future events** extending months ahead

---

**Your calendar will now automatically sync every 6 hours without any file modifications!** 🎯
