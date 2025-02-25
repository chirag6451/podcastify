import os
from datetime import datetime
from pathlib import Path
from typing import Tuple
from profile_utils import ProfileUtils

# Initialize ProfileUtils instance
profile_utils = ProfileUtils()

def get_output_path(filename: str, profile_name: str, customer_id: str, 
                   job_id: str,
                   theme: str = "default",
                   timestamp_format: str = "%Y%m%d_%H%M",
                   create_dir: bool = True) -> Tuple[str, str]:
    """
    Generate an output path for a file using the pattern:
    output_folder/{profile_name}/{customer_id}/timestamp_filename
    
    Args:
        filename (str): Name of the file to be written
        profile_name (str): Name of the profile being used
        customer_id (str): Customer identifier
        job_id (str): Unique job identifier
        theme (str, optional): Theme name to use. Defaults to "default".
        timestamp_format (str, optional): Format for timestamp. Defaults to "%Y%m%d_%H%M".
        create_dir (bool, optional): Whether to create the directory structure. Defaults to True.
    
    Returns:
        Tuple[str, str]: A tuple containing:
            - The complete file path (e.g., '/path/to/output/profile/customer/job_id/20250223_1800_video.mp4')
            - The output directory path (e.g., '/path/to/output/profile/customer/job_id')
    
    Example:
        >>> file_path, output_dir = get_output_path('video.mp4', 'default_profile', 'customer123', 'job456')
        >>> print(file_path)
        '/path/to/output/default_profile/customer123/job456/20250223_1800_video.mp4'
        >>> print(output_dir)
        '/path/to/output/default_profile/customer123/job456'
    """
    # Get profile configuration
    config = profile_utils.get_merged_config(profile_name, section="global", theme=theme)
    
    # Get output folder from config
    output_folder = config.get('output_dir')
    if not output_folder:
        raise KeyError("output_dir not defined in profile configuration")
    
    # Generate timestamp
    timestamp = datetime.now().strftime(timestamp_format)
    
    # Construct the paths
    output_dir = Path(output_folder) / profile_name / customer_id / str(job_id)
    output_path = output_dir / f"{timestamp}_{filename}"
    
    # Create directory if requested
    if create_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    return str(output_path), str(output_dir)
