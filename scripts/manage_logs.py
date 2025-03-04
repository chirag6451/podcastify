#!/usr/bin/env python3
"""Script to manage log files and clean up old logs."""
import os
import time
from datetime import datetime, timedelta
import glob

def cleanup_old_logs(log_dir: str, max_age_days: int = 7, max_size_mb: int = 100):
    """
    Clean up old log files.
    
    Args:
        log_dir: Directory containing log files
        max_age_days: Maximum age of log files in days
        max_size_mb: Maximum total size of log files in MB
    """
    if not os.path.exists(log_dir):
        print(f"Log directory {log_dir} does not exist")
        return
        
    # Get all log files
    log_files = glob.glob(os.path.join(log_dir, '*.log*'))
    
    # Remove files older than max_age_days
    cutoff_time = time.time() - (max_age_days * 86400)
    for log_file in log_files:
        if os.path.getmtime(log_file) < cutoff_time:
            try:
                os.remove(log_file)
                print(f"Removed old log file: {log_file}")
            except Exception as e:
                print(f"Error removing {log_file}: {e}")
    
    # Check total size and remove oldest files if needed
    while True:
        log_files = glob.glob(os.path.join(log_dir, '*.log*'))
        total_size = sum(os.path.getsize(f) for f in log_files)
        if total_size <= max_size_mb * 1024 * 1024:
            break
            
        # Get oldest file
        oldest_file = min(log_files, key=os.path.getmtime)
        try:
            os.remove(oldest_file)
            print(f"Removed oldest log file to reduce size: {oldest_file}")
        except Exception as e:
            print(f"Error removing {oldest_file}: {e}")
            break

if __name__ == '__main__':
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    cleanup_old_logs(log_dir)
