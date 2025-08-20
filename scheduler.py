import logging
from datetime import datetime, timedelta
from typing import Dict, List
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import os

logger = logging.getLogger(__name__)

class CalendarScheduler:
    """Handles automated scheduling of calendar synchronization"""
    
    def __init__(self, google_sync, subsplash_extractor):
        self.google_sync = google_sync
        self.subsplash_extractor = subsplash_extractor
        self.scheduler = BackgroundScheduler()
        self.last_sync = None
        self.sync_history = []
        self.is_running = False
        
        # Configuration
        self.sync_interval_hours = int(os.getenv('SYNC_INTERVAL_HOURS', '6'))
        self.subsplash_embed_code = os.getenv('SUBSPLASH_EMBED_CODE', '')
        
    def start(self):
        """Start the automated scheduler"""
        try:
            if self.is_running:
                logger.warning("Scheduler is already running")
                return
            
            # Add jobs to the scheduler
            self._add_sync_job()
            self._add_cleanup_job()
            
            # Start the scheduler
            self.scheduler.start()
            self.is_running = True
            
            logger.info("Calendar scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            raise
    
    def stop(self):
        """Stop the automated scheduler"""
        try:
            if not self.is_running:
                logger.warning("Scheduler is not running")
                return
            
            self.scheduler.shutdown()
            self.is_running = False
            
            logger.info("Calendar scheduler stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {str(e)}")
            raise
    
    def _add_sync_job(self):
        """Add the main synchronization job"""
        try:
            # Run every 6 hours by default (configurable)
            trigger = CronTrigger(
                hour=f"*/{self.sync_interval_hours}",
                minute=0,
                second=0
            )
            
            self.scheduler.add_job(
                func=self.sync_calendars,
                trigger=trigger,
                id='calendar_sync',
                name='Calendar Synchronization',
                replace_existing=True
            )
            
            logger.info(f"Added calendar sync job to run every {self.sync_interval_hours} hours")
            
        except Exception as e:
            logger.error(f"Failed to add sync job: {str(e)}")
            raise
    
    def _add_cleanup_job(self):
        """Add cleanup job to run daily"""
        try:
            # Run daily at 2 AM
            trigger = CronTrigger(hour=2, minute=0, second=0)
            
            self.scheduler.add_job(
                func=self._cleanup_old_logs,
                trigger=trigger,
                id='cleanup_job',
                name='Cleanup Old Logs',
                replace_existing=True
            )
            
            logger.info("Added cleanup job to run daily at 2 AM")
            
        except Exception as e:
            logger.error(f"Failed to add cleanup job: {str(e)}")
            raise
    
    def sync_calendars(self) -> Dict:
        """
        Main synchronization method that extracts from Subsplash and syncs to Google Calendar
        
        Returns:
            Dictionary with sync results
        """
        try:
            logger.info("Starting automated calendar synchronization")
            
            # Check if we have an embed code
            if not self.subsplash_embed_code:
                logger.warning("No Subsplash embed code configured. Skipping sync.")
                return {
                    'success': False,
                    'error': 'No Subsplash embed code configured',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Extract events from Subsplash
            logger.info("Extracting events from Subsplash calendar")
            subsplash_events = self.subsplash_extractor.extract_from_embed_code(
                self.subsplash_embed_code
            )
            
            if not subsplash_events:
                logger.warning("No events extracted from Subsplash")
                return {
                    'success': True,
                    'message': 'No events to sync',
                    'events_extracted': 0,
                    'timestamp': datetime.now().isoformat()
                }
            
            logger.info(f"Extracted {len(subsplash_events)} events from Subsplash")
            
            # Sync events to Google Calendar
            logger.info("Syncing events to Google Calendar")
            sync_results = self.google_sync.sync_events(subsplash_events)
            
            # Update internal state
            self.last_sync = datetime.now()
            sync_summary = {
                'success': True,
                'timestamp': self.last_sync.isoformat(),
                'events_extracted': len(subsplash_events),
                'sync_results': sync_results
            }
            
            # Add to history
            self.sync_history.append(sync_summary)
            
            # Keep only last 100 entries
            if len(self.sync_history) > 100:
                self.sync_history = self.sync_history[-100:]
            
            logger.info(f"Calendar synchronization completed successfully. "
                       f"Created: {sync_results['created']}, "
                       f"Updated: {sync_results['updated']}, "
                       f"Deleted: {sync_results['deleted']}, "
                       f"Errors: {sync_results['errors']}")
            
            return sync_summary
            
        except Exception as e:
            error_msg = f"Calendar synchronization failed: {str(e)}"
            logger.error(error_msg)
            
            # Record the error
            error_summary = {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            self.sync_history.append(error_summary)
            self.last_sync = datetime.now()
            
            return error_summary
    
    def manual_sync(self) -> Dict:
        """Trigger a manual synchronization"""
        logger.info("Manual calendar synchronization triggered")
        return self.sync_calendars()
    
    def _cleanup_old_logs(self):
        """Clean up old log entries and temporary files"""
        try:
            logger.info("Running cleanup job")
            
            # Clean up old sync history (keep only last 50 entries)
            if len(self.sync_history) > 50:
                self.sync_history = self.sync_history[-50:]
                logger.info("Cleaned up old sync history entries")
            
            # Clean up old token files if they exist
            token_files = ['token.pickle']
            for token_file in token_files:
                if os.path.exists(token_file):
                    # Check if token is older than 30 days
                    file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(token_file))
                    if file_age.days > 30:
                        os.remove(token_file)
                        logger.info(f"Removed old token file: {token_file}")
            
            logger.info("Cleanup job completed successfully")
            
        except Exception as e:
            logger.error(f"Cleanup job failed: {str(e)}")
    
    def get_status(self) -> Dict:
        """Get the current status of the scheduler"""
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                })
            
            return {
                'is_running': self.is_running,
                'last_sync': self.last_sync.isoformat() if self.last_sync else None,
                'sync_interval_hours': self.sync_interval_hours,
                'total_syncs': len(self.sync_history),
                'successful_syncs': len([s for s in self.sync_history if s.get('success', False)]),
                'failed_syncs': len([s for s in self.sync_history if not s.get('success', False)]),
                'jobs': jobs,
                'status': 'active' if self.is_running else 'stopped'
            }
            
        except Exception as e:
            logger.error(f"Failed to get scheduler status: {str(e)}")
            return {
                'is_running': False,
                'status': 'error',
                'error': str(e)
            }
    
    def get_sync_history(self, limit: int = 10) -> List[Dict]:
        """Get recent synchronization history"""
        try:
            return self.sync_history[-limit:] if self.sync_history else []
        except Exception as e:
            logger.error(f"Failed to get sync history: {str(e)}")
            return []
    
    def update_config(self, sync_interval_hours: int = None, subsplash_embed_code: str = None):
        """Update scheduler configuration"""
        try:
            if sync_interval_hours is not None:
                self.sync_interval_hours = sync_interval_hours
                logger.info(f"Updated sync interval to {sync_interval_hours} hours")
                
                # Restart scheduler to apply new interval
                if self.is_running:
                    self.stop()
                    self.start()
            
            if subsplash_embed_code is not None:
                self.subsplash_embed_code = subsplash_embed_code
                logger.info("Updated Subsplash embed code")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update scheduler config: {str(e)}")
            return False
    
    def test_subsplash_connection(self) -> Dict:
        """Test the connection to Subsplash and extract sample data"""
        try:
            if not self.subsplash_embed_code:
                return {
                    'success': False,
                    'error': 'No Subsplash embed code configured'
                }
            
            logger.info("Testing Subsplash connection")
            events = self.subsplash_extractor.extract_from_embed_code(
                self.subsplash_embed_code
            )
            
            return {
                'success': True,
                'events_found': len(events),
                'sample_events': events[:3] if events else [],  # Return first 3 events as sample
                'message': f"Successfully connected to Subsplash. Found {len(events)} events."
            }
            
        except Exception as e:
            logger.error(f"Subsplash connection test failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
