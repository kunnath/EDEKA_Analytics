"""
Logging utilities for the EDEKA analytics application.
"""
import os
import sys
from datetime import datetime
from loguru import logger

def setup_logger():
    """Configure the logger for the application."""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Generate log filename with timestamp
    log_filename = os.path.join(logs_dir, f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Configure loguru
    config = {
        "handlers": [
            {"sink": sys.stdout, "format": "{time} | {level} | {message}", "level": "INFO"},
            {"sink": log_filename, "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", "level": "DEBUG"},
        ],
    }
    
    # Remove default handler and apply our configuration
    logger.remove()
    for handler in config["handlers"]:
        logger.add(**handler)
    
    return logger

# Create a global logger instance
logger = setup_logger()
