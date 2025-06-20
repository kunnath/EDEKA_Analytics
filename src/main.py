#!/usr/bin/env python3
"""
Main entry point for the EDEKA analytics database synchronization tool.
"""
import argparse
import sys
import time
from dotenv import load_dotenv

from src.integrations.external_db_sync import DatabaseSyncManager
from src.integrations.scheduler import start_scheduler
from src.utils.logger import logger

# Load environment variables
load_dotenv()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='EDEKA Analytics DB Sync Tool')
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Run a one-time sync')
    sync_parser.add_argument('--table', help='Specific table to sync (default: all tables)')
    
    # Scheduler command
    scheduler_parser = subparsers.add_parser('scheduler', help='Start the sync scheduler')
    scheduler_parser.add_argument('--daemon', action='store_true', help='Run as daemon process')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize the database schema')
    
    return parser.parse_args()

def run_sync(table_name=None):
    """Run a one-time sync."""
    sync_manager = DatabaseSyncManager()
    
    if table_name:
        logger.info(f"Running sync for table: {table_name}")
        result = sync_manager.sync_table(table_name)
        logger.info(f"Sync completed for {table_name}: fetched={result[0]}, inserted={result[1]}, updated={result[2]}, failed={result[3]}")
    else:
        logger.info("Running sync for all tables")
        result = sync_manager.sync_external_data()
        logger.info(f"Sync completed: {result}")
    
    return result

def init_db():
    """Initialize the database schema."""
    from src.utils.db_utils import get_internal_db_engine
    from src.models.database import init_db
    
    logger.info("Initializing database schema")
    engine = get_internal_db_engine()
    init_db(engine)
    logger.info("Database schema initialized successfully")

def main():
    """Main function to handle command line interface."""
    args = parse_args()
    
    if args.command == 'sync':
        run_sync(args.table)
    
    elif args.command == 'scheduler':
        logger.info("Starting scheduler")
        scheduler = start_scheduler()
        
        try:
            # Keep the process running
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Stopping scheduler")
            scheduler.shutdown()
    
    elif args.command == 'init':
        init_db()
    
    else:
        # If no command is provided, show help
        logger.error("No command specified")
        sys.exit(1)

if __name__ == "__main__":
    main()
