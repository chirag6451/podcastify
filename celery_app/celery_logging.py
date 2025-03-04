"""Celery logging configuration with rotating file handler."""
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

def setup_celery_logging():
    """Setup Celery logging with rotating file handler."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure rotating file handler
    log_file = os.path.join(log_dir, 'celery_tasks.log')
    handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB per file
        backupCount=5,  # Keep 5 backup files
        encoding='utf-8'
    )
    
    # Set formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - Job %(job_id)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Get celery logger
    logger = logging.getLogger('celery')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    # Also log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

class TaskLogger:
    """Context manager for task logging with job ID."""
    
    def __init__(self, job_id):
        self.job_id = job_id
        self.logger = logging.getLogger('celery')
        self.extra = {'job_id': job_id}
    
    def info(self, message):
        """Log info message with job ID context."""
        self.logger.info(message, extra=self.extra)
    
    def error(self, message):
        """Log error message with job ID context."""
        self.logger.error(message, extra=self.extra)
    
    def debug(self, message):
        """Log debug message with job ID context."""
        self.logger.debug(message, extra=self.extra)
    
    def warning(self, message):
        """Log warning message with job ID context."""
        self.logger.warning(message, extra=self.extra)
