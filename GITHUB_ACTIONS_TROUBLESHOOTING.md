# GitHub Actions Troubleshooting Guide

## Why GitHub Actions Fails While Local Tests Work

### 1. **Browser Environment Differences**
- **Local**: Runs with visible browser, full Chrome features
- **GitHub Actions**: Runs headless, limited Chrome features, different OS (Ubuntu vs Windows)

### 2. **Chrome Installation Issues**
- **Local**: Full Chrome installation with all dependencies
- **GitHub Actions**: Minimal Chrome installation, missing fonts, libraries

### 3. **Timing and Rendering Differences**
- **Local**: Slower rendering, more forgiving timing
- **GitHub Actions**: Faster rendering, stricter timing requirements

### 4. **Resource Limitations**
- **Local**: Full system resources
- **GitHub Actions**: Limited CPU/memory, shared runner environment

## Solutions Implemented

### ✅ **Updated GitHub Actions Workflow**
- Proper Chrome installation with system dependencies
- Enhanced browser configuration for headless environment
- Better error handling and debugging

### ✅ **Enhanced Browser Setup**
- Different Chrome options for GitHub Actions vs local
- Proper Chrome path detection
- Enhanced error logging

### ✅ **Test Script for GitHub Actions Simulation**
- `test_github_actions.py` - Test headless mode locally
- Simulates GitHub Actions environment
- Helps debug issues before deployment

## Testing Steps

### 1. **Test Headless Mode Locally**
```bash
python test_github_actions.py --headless
```

### 2. **Check Chrome Installation**
```bash
# Verify Chrome is installed
google-chrome --version

# Check Chrome path
which google-chrome
```

### 3. **Test with Minimal Dependencies**
```bash
# Install only essential packages
pip install selenium beautifulsoup4 requests
```

## Common Issues and Fixes

### Issue: Chrome Driver Not Found
**Fix**: Use system Chrome instead of ChromeDriverManager in GitHub Actions
```python
if is_github_actions:
    service = Service('/usr/bin/google-chrome')
else:
    service = Service(ChromeDriverManager().install())
```

### Issue: Page Elements Not Loading
**Fix**: Increase wait times and add explicit waits
```python
# Set longer timeouts for headless mode
self.browser.set_page_load_timeout(30)
self.browser.implicitly_wait(10)
```

### Issue: JavaScript Not Executing
**Fix**: Add Chrome flags for headless mode
```python
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument('--disable-features=VizDisplayCompositor')
```

## Alternative Approaches

### Option 1: **Fix GitHub Actions (Recommended)**
- ✅ Automated, runs every 6 hours
- ✅ No manual intervention needed
- ✅ Centralized logging and monitoring
- ❌ More complex setup
- ❌ Requires debugging headless environment

### Option 2: **Host on Your Website**
- ✅ Simpler setup
- ✅ Full browser environment
- ✅ Easier debugging
- ❌ Requires hosting infrastructure
- ❌ Manual execution needed
- ❌ Less reliable scheduling

### Option 3: **Hybrid Approach**
- Use GitHub Actions for basic scraping
- Host complex operations on your website
- Best of both worlds

## Debugging Commands

### Check GitHub Actions Logs
```bash
# Look for these error patterns:
- "Chrome version check failed"
- "Browser setup failed"
- "Page load timeout"
- "Element not found"
```

### Test Specific Components
```bash
# Test browser setup only
python -c "from sync_script import SubsplashCalendarSync; s = SubsplashCalendarSync(); print(s.setup_browser())"

# Test page loading only
python -c "from sync_script import SubsplashCalendarSync; s = SubsplashCalendarSync(); s.setup_browser(); s.browser.get('https://antiochboone.com/calendar-prayer')"
```

## Next Steps

1. **Run the test script locally in headless mode**
2. **Check if the updated workflow fixes the issues**
3. **Monitor GitHub Actions logs for specific error messages**
4. **Consider the hybrid approach if issues persist**

## Why This Should Work

The key differences between your local tests and GitHub Actions have been addressed:

- ✅ **Chrome Installation**: Proper system Chrome instead of ChromeDriverManager
- ✅ **Browser Options**: Headless-optimized Chrome flags
- ✅ **Timing**: Increased wait times for headless environment
- ✅ **Error Handling**: Better debugging and logging
- ✅ **Environment Detection**: Different behavior for GitHub Actions vs local

Your local tests work because they have a full Chrome environment. The updated GitHub Actions workflow now provides the same robust Chrome installation with headless-optimized settings.
