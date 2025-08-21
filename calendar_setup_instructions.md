# FullCalendar Widget Setup Instructions

## Overview
This FullCalendar widget provides a powerful, feature-rich calendar interface that integrates with your Google Calendars, offering much more functionality than the native Subsplash calendar.

## Features Implemented

### ✅ Core Requirements
- **Calendar Toggle**: Individual on/off switches for each calendar
- **Select All / Deselect All**: Quick bulk selection controls
- **Multiple Views**: Monthly, Quarterly (3-month), Annual, and List views
- **Search Functionality**: Search events by title, description, or location

### ✅ Additional Features
- **Event Details Modal**: Click any event to see full details
- **Color Coding**: Each calendar type has its own color scheme
- **Responsive Design**: Mobile-friendly interface
- **Event Sharing**: Native sharing or clipboard copy
- **Add to Calendar**: Integration with personal calendars
- **Modern UI**: Clean, professional design with smooth animations

## Setup Steps

### 1. Get Google Calendar API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Calendar API
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy your API key

### 2. Update Calendar Configuration

In `fullcalendar_widget.html`, find this section and update with your actual calendar IDs:

```javascript
const CONFIG = {
    // Replace with your actual Google Calendar API key
    GOOGLE_API_KEY: 'YOUR_ACTUAL_API_KEY_HERE',
    
    // Update these with your actual calendar IDs from your sync script
    CALENDARS: {
        'prayer': 'your_actual_prayer_calendar_id@group.calendar.google.com',
        'men': 'your_actual_men_calendar_id@group.calendar.google.com',
        // ... update all calendar IDs
    }
};
```

### 3. Deploy to Your Website

#### Option A: Direct HTML File
1. Upload `fullcalendar_widget.html` to your web server
2. Access it directly via URL

#### Option B: Embed in Existing Page
1. Copy the HTML content from the `<body>` section
2. Copy the CSS from the `<style>` section
3. Copy the JavaScript from the `<script>` section
4. Paste into your existing webpage

#### Option C: iFrame Embed
```html
<iframe src="path/to/fullcalendar_widget.html" 
        width="100%" 
        height="800px" 
        frameborder="0"
        style="border: none; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
</iframe>
```

## Calendar ID Format

Your calendar IDs should look like one of these formats:
- `calendar_id@group.calendar.google.com` (for shared calendars)
- `your_email@gmail.com` (for personal calendars)
- `random_string@group.calendar.google.com` (for public calendars)

## Troubleshooting

### Common Issues

1. **Events Not Loading**
   - Check your API key is correct
   - Verify calendar IDs are correct
   - Ensure calendars are public or shared
   - Check browser console for errors

2. **API Quota Exceeded**
   - Google Calendar API has daily limits
   - Consider implementing caching
   - Monitor usage in Google Cloud Console

3. **Styling Issues**
   - Ensure all CSS is loaded
   - Check for conflicting styles on your website
   - Verify FullCalendar CSS files are accessible

### Debug Mode

Add this to your browser console to see detailed information:
```javascript
localStorage.setItem('fcDebug', 'true');
```

## Customization Options

### Colors
Update the color scheme in the CSS section:
```css
:root {
    --primary-color: #your-color;
    --secondary-color: #your-color;
    /* ... other colors */
}
```

### Calendar Colors
Modify the calendar-specific colors in the JavaScript:
```javascript
function getCalendarColor(calendarId) {
    const colors = {
        'prayer': '#your-color',
        'men': '#your-color',
        // ... update colors
    };
    return colors[calendarId] || '#default-color';
}
```

### Views
Add or modify calendar views:
```javascript
views: {
    customView: {
        type: 'dayGrid',
        duration: { months: 6 },
        buttonText: '6 Months'
    }
}
```

## Performance Optimization

### For High-Event Calendars
1. **Implement Pagination**: Load events month by month
2. **Add Caching**: Store events in localStorage
3. **Lazy Loading**: Load events as needed
4. **Event Limits**: Set `dayMaxEvents` to reasonable numbers

### Example Caching Implementation
```javascript
// Add to your calendar configuration
eventSourceSuccess: function(content, xhr) {
    // Cache events
    localStorage.setItem('calendar_cache', JSON.stringify(content));
},
eventSourceFailure: function(error) {
    // Try to load from cache
    const cached = localStorage.getItem('calendar_cache');
    if (cached) {
        return JSON.parse(cached);
    }
}
```

## Security Considerations

1. **API Key Protection**
   - Restrict API key to your domain
   - Set appropriate quotas
   - Monitor usage regularly

2. **Calendar Privacy**
   - Ensure sensitive calendars are private
   - Use appropriate sharing settings
   - Regular access reviews

## Maintenance

### Regular Tasks
1. **Monitor API Usage**: Check Google Cloud Console monthly
2. **Update Dependencies**: Keep FullCalendar versions current
3. **Test Functionality**: Verify all features work after updates
4. **Backup Configuration**: Keep copies of your calendar IDs

### Updates
- FullCalendar releases updates regularly
- Test new versions in development first
- Keep backup of working version

## Support Resources

- [FullCalendar Documentation](https://fullcalendar.io/docs)
- [Google Calendar API Docs](https://developers.google.com/calendar)
- [Google Cloud Console](https://console.cloud.google.com/)

## File Structure

```
SubsplashCalendarBridge/
├── fullcalendar_widget.html          # Main calendar widget
├── calendar_setup_instructions.md    # This setup guide
├── sync_script.py                   # Your existing sync script
└── config.env.example               # Environment configuration
```

## Next Steps

1. **Test Locally**: Open the HTML file in your browser first
2. **Configure API**: Add your Google Calendar API key
3. **Update IDs**: Replace calendar IDs with your actual ones
4. **Deploy**: Upload to your web server
5. **Customize**: Adjust colors, styling, and features as needed
6. **Monitor**: Watch for any issues and optimize performance

## Questions?

If you encounter any issues or need help with customization, check the troubleshooting section above or refer to the FullCalendar and Google Calendar API documentation.
