"""
Scheduler for running database synchronization at regular intervals.
"""
import os
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from src.integrations.external_db_sync import DatabaseSyncManager
from src.utils.logger import logger

# Load environment variables
load_dotenv()

def get_sync_interval():
    """Get the sync interval from environment variables."""
    interval = os.getenv('SYNC_INTERVAL_MINUTES', '60')
    try:
        return int(interval)
    except ValueError:
        logger.warning(f"Invalid sync interval: {interval}. Using default: 60")
        return 60

def scheduled_sync_job():
    """Run the sync job and log the results."""
    logger.info("Starting scheduled sync job")
    sync_manager = DatabaseSyncManager()
    result = sync_manager.sync_external_data()
    
    logger.info(f"Scheduled sync completed: {result}")
    return result

def start_scheduler():
    """Start the background scheduler for regular sync jobs."""
    interval = get_sync_interval()
    logger.info(f"Setting up scheduler to run every {interval} minutes")
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_sync_job, 'interval', minutes=interval, id='sync_job')
    scheduler.start()
    
    logger.info("Scheduler started")
    return scheduler

if __name__ == "__main__":
    logger.info("Starting sync scheduler as standalone process")
    scheduler = start_scheduler()
    
    try:
        # Keep the script running
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping scheduler")
        scheduler.shutdown()
