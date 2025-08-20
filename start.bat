@echo off
echo Starting Subsplash Calendar Bridge...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher and try again
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if .env file exists
if not exist ".env" (
    echo Warning: .env file not found
    echo Please copy config.env.example to .env and configure it
    echo.
)

REM Check if credentials.json exists
if not exist "credentials.json" (
    echo Warning: credentials.json not found
    echo Please download Google Calendar API credentials and save as credentials.json
    echo.
)

echo Starting application...
echo Dashboard will be available at: http://localhost:5000
echo Press Ctrl+C to stop the application
echo.

python app.py

pause
