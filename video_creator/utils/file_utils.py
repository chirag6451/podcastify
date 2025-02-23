import os
import random
from typing import List, Optional

def get_random_file(directory: str, extensions: Optional[List[str]] = None) -> str:
    """
    Get a random file from the specified directory with optional extension filtering.
    
    Args:
        directory: Directory path to search in
        extensions: List of file extensions to filter by (e.g., ['.mp3', '.wav'])
                   If None, all files are considered
    
    Returns:
        Full path to the randomly selected file
    
    Raises:
        ValueError: If no matching files are found in the directory
    """
    if not os.path.exists(directory):
        raise ValueError(f"Directory does not exist: {directory}")
    
    # Get all files in directory
    all_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    # Filter by extensions if specified
    if extensions:
        matching_files = [f for f in all_files if any(f.lower().endswith(ext.lower()) for ext in extensions)]
    else:
        matching_files = all_files
    
    if not matching_files:
        raise ValueError(f"No matching files found in directory: {directory}")
    
    # Select random file
    selected_file = random.choice(matching_files)
    return os.path.join(directory, selected_file)
