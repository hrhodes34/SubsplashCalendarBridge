#!/usr/bin/env python3
"""
Simple Calendar Sync Server
Run this locally to handle sync requests from the Subsplash sync button
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from your Subsplash page

class SimpleSyncServer:
    def __init__(self):
        self.sync_script_path = 'sync_script.py'
        self.is_syncing = False
        self.last_sync_time = None
        self.last_sync_result = None
        
    def run_sync(self, calendars, months_to_check):
        """Run the sync script with specified parameters"""
        if self.is_syncing:
            return {"error": "Sync already in progress"}
            
        try:
            self.is_syncing = True
            
            # Set environment variables for the sync script
            env = os.environ.copy()
            env['MAX_MONTHS_TO_CHECK'] = str(months_to_check)
            env['SELECTED_CALENDARS'] = ','.join(calendars)
            
            # Run the sync script
            logger.info(f"Starting sync for calendars: {calendars}")
            
            result = subprocess.run(
                [sys.executable, self.sync_script_path],
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.last_sync_result = {
                    "success": True,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                logger.info("Sync completed successfully")
            else:
                self.last_sync_result = {
                    "success": False,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode
                }
                logger.error(f"Sync failed with return code {result.returncode}")
                
            self.last_sync_time = datetime.now().isoformat()
            return self.last_sync_result
            
        except subprocess.TimeoutExpired:
            error_msg = "Sync timed out after 5 minutes"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Sync error: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        finally:
            self.is_syncing = False

# Create sync server instance
sync_server = SimpleSyncServer()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "is_syncing": sync_server.is_syncing
    })

@app.route('/sync', methods=['POST'])
def start_sync():
    """Start a calendar sync"""
    try:
        data = request.get_json()
        calendars = data.get('calendars', [])
        months_to_check = data.get('months_to_check', 6)
        
        if not calendars:
            return jsonify({"error": "No calendars specified"}), 400
            
        logger.info(f"Sync request received: {calendars} calendars, {months_to_check} months")
        
        # Run the sync
        result = sync_server.run_sync(calendars, months_to_check)
        
        if "error" in result:
            return jsonify(result), 500
        else:
            return jsonify({
                "success": True,
                "result": result,
                "timestamp": sync_server.last_sync_time
            })
            
    except Exception as e:
        logger.error(f"Error handling sync request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get current sync status"""
    return jsonify({
        "is_syncing": sync_server.is_syncing,
        "last_sync_time": sync_server.last_sync_time,
        "last_sync_result": sync_server.last_sync_result
    })

@app.route('/calendars', methods=['GET'])
def get_available_calendars():
    """Get list of available calendars"""
    # This would typically come from your environment variables
    calendars = {
        'prayer': 'Prayer Calendar',
        'bam': 'BAM Calendar', 
        'kids': 'Kids Calendar',
        'college': 'College Calendar',
        'youth': 'Youth Calendar',
        'women': 'Women\'s Calendar',
        'men': 'Men\'s Calendar',
        'missions': 'Missions Calendar',
        'worship': 'Worship Calendar',
        'teaching': 'Teaching Calendar',
        'churchwide': 'Churchwide Calendar'
    }
    
    return jsonify(calendars)

if __name__ == '__main__':
    print("🚀 Starting Simple Calendar Sync Server")
    print("📱 Server will be available at: http://localhost:5000")
    print("🔗 Health check: http://localhost:5000/health")
    print("📊 Sync endpoint: http://localhost:5000/sync")
    print("📋 Status endpoint: http://localhost:5000/status")
    print("📅 Calendars endpoint: http://localhost:5000/calendars")
    print("\n💡 To use this with your Subsplash sync button:")
    print("   1. Update the CALENDAR_IDS in your HTML")
    print("   2. Change the simulateSync function to call this server")
    print("   3. Run this server when you want to sync")
    print("\n⏹️  Press Ctrl+C to stop the server\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
