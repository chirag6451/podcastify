import logging
import sys
from pathlib import Path

class PodcastLogger:
    def __init__(self, name: str, log_file: str = None):
        self.logger = self._setup_logger(name, log_file)
    
    def _setup_logger(self, name: str, log_file: str = None) -> logging.Logger:
        """Set up a logger with both file and console handlers"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (if log_file is provided)
        if log_file:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            file_handler = logging.FileHandler(log_dir / log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def success(self, message: str):
        self.logger.info(f" {message}")

# Create API logger instance
api_logger = PodcastLogger("api", "api.log")
