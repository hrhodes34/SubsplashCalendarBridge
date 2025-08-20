# Subsplash Calendar Bridge

A comprehensive solution for automatically syncing Subsplash calendar data with Google Calendar and providing enhanced calendar views for your website.

## 🚀 Features

- **Automatic Calendar Sync**: Automatically extracts events from Subsplash and syncs them to Google Calendar
- **Enhanced Calendar Views**: Provides weekly, monthly, quarterly, and annual calendar views
- **Embeddable Widgets**: Easy-to-embed calendar widgets for your Subsplash website
- **Automated Operation**: Runs maintenance-free with configurable sync intervals
- **Modern Web Interface**: Beautiful dashboard for monitoring and controlling the sync process
- **Real-time Status**: Live monitoring of sync status and calendar health

## 📋 Prerequisites

- Python 3.8 or higher
- Google Calendar API access
- Subsplash calendar embed code
- Web server (for production deployment)

## 🛠️ Installation

### 1. Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd SubsplashCalendarBridge

# Or simply download and extract the files
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Google Calendar API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials file and save it as `credentials.json` in the project root
6. Place the file in the project directory

### 4. Configure Environment Variables

Copy `config.env.example` to `.env` and update the values:

```bash
cp config.env.example .env
```

Edit `.env` with your actual values:

```env
# Flask Configuration
SECRET_KEY=your-very-secure-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False

# Google Calendar API Configuration
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_CALENDAR_ID=primary

# Subsplash Configuration
SUBSPLASH_EMBED_CODE=your-actual-subsplash-embed-code-here

# Scheduler Configuration
SYNC_INTERVAL_HOURS=6

# Server Configuration
HOST=0.0.0.0
PORT=5000
```

### 5. First Run Setup

On first run, the application will:
1. Open a browser window for Google Calendar authentication
2. Ask you to authorize the application
3. Create a `token.pickle` file for future authentication

## 🚀 Usage

### Starting the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Dashboard Access

- **Main Dashboard**: `http://localhost:5000/`
- **Calendar Widgets**: 
  - Weekly: `http://localhost:5000/widget/weekly`
  - Monthly: `http://localhost:5000/widget/monthly`
  - Quarterly: `http://localhost:5000/widget/quarterly`
  - Annual: `http://localhost:5000/widget/annually`

### Manual Operations

- **Manual Sync**: Click "Manual Sync Now" in the dashboard
- **Test Connection**: Click "Test Connection" to verify Subsplash connectivity
- **View Status**: Monitor real-time sync status and history

## 🔧 Configuration

### Sync Interval

The default sync interval is 6 hours. You can modify this in the `.env` file:

```env
SYNC_INTERVAL_HOURS=12  # Sync every 12 hours
```

### Google Calendar ID

By default, the application uses your primary calendar. To use a specific calendar:

```env
GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com
```

### Subsplash Embed Code

Update the `SUBSPLASH_EMBED_CODE` variable with your actual Subsplash calendar embed code.

## 🌐 Embedding in Your Website

### Widget Embed Codes

Use these iframe codes to embed enhanced calendar views on your Subsplash website:

```html
<!-- Weekly View -->
<iframe src="http://your-domain.com/widget/weekly" width="100%" height="600" frameborder="0"></iframe>

<!-- Monthly View -->
<iframe src="http://your-domain.com/widget/monthly" width="100%" height="600" frameborder="0"></iframe>

<!-- Quarterly View -->
<iframe src="http://your-domain.com/widget/quarterly" width="100%" height="600" frameborder="0"></iframe>

<!-- Annual View -->
<iframe src="http://your-domain.com/widget/annually" width="100%" height="600" frameborder="0"></iframe>
```

### Customization

You can customize the widget appearance by modifying the CSS in `templates/widget.html`.

## 🚀 Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:

```bash
docker build -t subsplash-calendar-bridge .
docker run -p 5000:5000 subsplash-calendar-bridge
```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Monitoring and Maintenance

### Dashboard Features

- **Real-time Status**: Monitor scheduler and sync status
- **Sync History**: View recent sync operations and results
- **Calendar Preview**: Test different calendar views
- **Error Logging**: Track and resolve sync issues

### Logs

The application logs all operations. Check the console output or redirect to a log file:

```bash
python app.py > app.log 2>&1
```

### Health Checks

The application provides several health check endpoints:

- `/api/scheduler/status` - Scheduler status
- `/api/subsplash/status` - Subsplash connection status
- `/api/calendar/sync` - Manual sync trigger

## 🔒 Security Considerations

- **Environment Variables**: Never commit `.env` files to version control
- **Google Credentials**: Keep `credentials.json` and `token.pickle` secure
- **Network Security**: Use HTTPS in production
- **Access Control**: Consider implementing authentication for the dashboard

## 🐛 Troubleshooting

### Common Issues

1. **Google Calendar Authentication Failed**
   - Delete `token.pickle` and re-authenticate
   - Verify `credentials.json` is correct

2. **Subsplash Events Not Extracting**
   - Check the embed code format
   - Verify Subsplash calendar is accessible
   - Check network connectivity

3. **Sync Not Running**
   - Verify scheduler is started
   - Check environment variables
   - Review error logs

### Debug Mode

Enable debug mode for detailed error information:

```env
FLASK_DEBUG=True
FLASK_ENV=development
```

## 📈 Performance Optimization

- **Sync Frequency**: Adjust `SYNC_INTERVAL_HOURS` based on your needs
- **Database**: Consider adding a database for better event management
- **Caching**: Implement Redis for caching calendar data
- **Load Balancing**: Use multiple worker processes with Gunicorn

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check the troubleshooting section
2. Review the logs for error details
3. Open an issue on the repository
4. Contact the development team

## 🔄 Updates and Maintenance

The application is designed to run maintenance-free, but regular updates are recommended:

- **Security Updates**: Keep dependencies updated
- **Feature Updates**: Monitor for new features and improvements
- **Backup**: Regularly backup configuration and token files

---

**Note**: This application automatically handles Google Calendar authentication tokens and will refresh them as needed. The first run requires manual authentication through a web browser.
