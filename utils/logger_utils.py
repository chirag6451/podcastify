import logging
import sys
import os
import inspect
from datetime import datetime
from typing import Optional

# ANSI escape codes for colors
class Colors:
    HEADER = '\033[95m'
    INFO = '\033[94m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors"""
    
    def __init__(self, fmt: str, include_line_info: bool = False):
        super().__init__()
        self.fmt = fmt
        self.include_line_info = include_line_info
        self.FORMATS = {
            logging.DEBUG: Colors.HEADER + fmt + Colors.ENDC,
            logging.INFO: Colors.INFO + fmt + Colors.ENDC,
            logging.WARNING: Colors.WARNING + fmt + Colors.ENDC,
            logging.ERROR: Colors.ERROR + fmt + Colors.ENDC,
            logging.CRITICAL: Colors.ERROR + Colors.BOLD + fmt + Colors.ENDC
        }

    def format(self, record):
        # Add line break decoration for all messages
        record.message = record.getMessage()
        
        # Add file and line info for errors and critical messages
        if self.include_line_info and record.levelno >= logging.ERROR:
            file_info = f"{Colors.BOLD}[{record.filename}:{record.lineno}]{Colors.ENDC} "
            record.message = file_info + record.message
        
        # Add spacing and line decoration
        record.message = f"\n++++ {record.message} ++++\n"
        
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class PodcastLogger:
    """Custom logger for the podcast application"""
    
    def __init__(self, name: str, log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Create formatters
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            include_line_info=True
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if log file is specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def _get_caller_info(self):
        """Get the caller's filename and line number"""
        frame = inspect.currentframe()
        caller_frame = frame.f_back.f_back  # Go back two frames to get the actual caller
        filename = os.path.basename(caller_frame.f_code.co_filename)
        lineno = caller_frame.f_lineno
        return filename, lineno
    
    def debug(self, msg: str):
        self.logger.debug(msg)
    
    def info(self, msg: str):
        self.logger.info(msg)
    
    def success(self, msg: str):
        """Custom success level - same as info but with green color"""
        self.logger.info(Colors.SUCCESS + msg + Colors.ENDC)
    
    def warning(self, msg: str):
        self.logger.warning(msg)
    
    def error(self, msg: str):
        filename, lineno = self._get_caller_info()
        self.logger.error(f"{msg}")
    
    def critical(self, msg: str):
        filename, lineno = self._get_caller_info()
        self.logger.critical(f"{msg}")
    
    def section(self, title: str):
        """Create a section break with a title"""
        line = "=" * 50
        self.info(f"\n{line}\n{title}\n{line}")
    
    def process_start(self, process_name: str):
        """Log the start of a process"""
        self.info(f"Starting process: {Colors.BOLD}{process_name}{Colors.ENDC}")
    
    def process_end(self, process_name: str, success: bool = True, duration: Optional[float] = None):
        """Log the end of a process with optional duration"""
        status = "completed successfully" if success else "failed"
        duration_str = f" in {duration:.2f} seconds" if duration is not None else ""
        if success:
            self.success(f"Process {process_name} {status}{duration_str}")
        else:
            self.error(f"Process {process_name} {status}{duration_str}")
    
    def progress(self, current: int, total: int, process_name: str):
        """Log progress of a process"""
        percentage = (current / total) * 100
        self.info(f"{process_name} Progress: {percentage:.1f}% ({current}/{total})")

    def separator(self, char: str = "-", length: int = 50):
        """Print a separator line"""
        self.info(char * length)
