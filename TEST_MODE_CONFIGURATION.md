# Test Mode Configuration for Focused Testing

## 🧪 **What is Test Mode?**

Test Mode is a temporary configuration that focuses the sync system on **only**:
- **One calendar**: Prayer calendar (`antiochboone.com/calendar-prayer`)
- **One month**: August 2025
- **Faster execution**: No multi-month navigation
- **Focused testing**: Easier to debug and verify

## 🎯 **Test Mode Configuration**

### **Environment Variables**
```bash
TEST_MODE=true                    # Enable test mode
MAX_MONTHS_TO_CHECK=1            # Only check 1 month
```

### **What Gets Scraped**
- **Calendar**: Prayer calendar only
- **Month**: August 2025 only
- **Events**: Early Morning Prayer (6:30a), Prayer Set (5:15p), etc.
- **Time Fix**: 4-hour offset correction applied

### **What Gets Skipped**
- All other calendars (BAM, Kids, College, etc.)
- Multiple month navigation
- Complex recurring event detection

## 🚀 **How to Enable Test Mode**

### **1. Local Testing**
```bash
# Set environment variable
export TEST_MODE=true

# Run sync script
python sync_script.py
```

### **2. GitHub Actions**
The workflow automatically sets:
```yaml
- name: Setup environment
  run: |
    cat > .env << EOF
    TEST_MODE=true
    MAX_MONTHS_TO_CHECK=1
    # ... other config
    EOF
```

## 📊 **Test Mode vs Production Mode**

| Feature | Test Mode | Production Mode |
|---------|-----------|-----------------|
| **Calendars** | Prayer only | All 18 calendars |
| **Months** | August 2025 only | 6+ months |
| **Navigation** | Direct to August | Month-by-month |
| **Execution Time** | ~2-3 minutes | ~10-15 minutes |
| **Debugging** | Focused, simple | Complex, multi-layered |

## 🧪 **Testing the Test Mode**

### **Local Verification**
```bash
python test_local_test_mode.py
```

**Expected Output:**
```
🧪 TEST MODE ENABLED - Only scraping prayer calendar for August
🎯 Target: August 2025 - Prayer Calendar Only
✅ Test Mode: True
🎯 Target Month: August
🎯 Target Year: 2025
📊 Max Months to Check: 1
📅 Calendar IDs: ['prayer']
🔗 Calendar URLs: ['prayer']
```

### **Full Mock Scrape Test**
```bash
python test_github_mock_scrape.py
```

This tests the complete scraping process in test mode.

## 🔧 **How Test Mode Works**

### **1. Initialization**
```python
# TEST MODE: Only prayer calendar for testing
self.test_mode = os.getenv('TEST_MODE', 'true').lower() == 'true'

if self.test_mode:
    self.calendar_ids = {'prayer': os.getenv('PRAYER_CALENDAR_ID')}
    self.calendar_urls = {'prayer': 'https://antiochboone.com/calendar-prayer'}
    self.max_months_to_check = 1
    self.target_month = 'August'
    self.target_year = '2025'
```

### **2. Scraping Logic**
```python
if self.test_mode:
    # TEST MODE: Only scrape August
    events = self._scrape_august_events(calendar_type)
else:
    # Production mode: Check multiple months
    # ... multi-month logic
```

### **3. August Navigation**
```python
def _navigate_to_august(self) -> bool:
    """TEST MODE: Navigate to August 2025"""
    # Look for next month button
    # Click forward until August 2025 is found
    # Return success/failure
```

## 📋 **Expected Test Results**

### **Events Found**
- **Early Morning Prayer**: 6:30a → 2:30 AM (after 4-hour offset)
- **Prayer Set**: 5:15p → 1:15 PM (after 4-hour offset)
- **Total Events**: ~24 events in August

### **Time Offset Verification**
```
✅ Early Morning Prayer: Correctly corrected from 6:30a to 2:30
✅ Prayer Set: Correctly corrected from 5:15p to 13:15
🎉 All time offset corrections verified successfully!
```

## 🚀 **Deploying Test Mode**

### **1. Commit Changes**
```bash
git add sync_script.py .github/workflows/sync_calendar.yml
git commit -m "Add test mode for focused August prayer calendar testing"
git push origin main
```

### **2. GitHub Actions Will**
- Run automatically every 6 hours
- Use test mode configuration
- Only scrape August prayer calendar
- Apply 4-hour time offset fix
- Sync events to Google Calendar

### **3. Monitor Results**
- Check GitHub Actions logs
- Verify events appear at correct times
- Confirm 4-hour offset fix is working

## 🔄 **Switching Back to Production**

### **1. Disable Test Mode**
```bash
# In GitHub Actions workflow
TEST_MODE=false
MAX_MONTHS_TO_CHECK=6
```

### **2. Or Remove Test Mode**
```bash
# Remove TEST_MODE environment variable
# System will default to production mode
```

## ⚠️ **Important Notes**

1. **Test Mode is Temporary**: Designed for focused testing only
2. **Limited Scope**: Only August prayer calendar
3. **Faster Execution**: Perfect for debugging time offset issues
4. **Easy Rollback**: Can switch back to production anytime
5. **GitHub Actions Ready**: Configured for automated testing

## 🎉 **Benefits of Test Mode**

1. **Focused Testing**: Only one calendar, one month
2. **Faster Execution**: No multi-month navigation
3. **Easier Debugging**: Simpler logic flow
4. **Time Offset Verification**: Perfect for testing the 4-hour fix
5. **GitHub Actions Testing**: Verify the complete pipeline works

## 🚀 **Ready for Testing!**

Your sync system is now configured for focused testing:
- ✅ **Test Mode Enabled**: Only August prayer calendar
- ✅ **4-Hour Time Fix**: Applied to all events
- ✅ **GitHub Actions Ready**: Automated testing pipeline
- ✅ **Focused Scope**: Easy to debug and verify

Test mode will run automatically via GitHub Actions and verify that your 4-hour time offset fix is working correctly in production!
