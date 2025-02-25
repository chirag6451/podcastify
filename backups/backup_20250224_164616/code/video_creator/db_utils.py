import os
import psycopg2
from psycopg2.extras import DictCursor
from typing import Dict, List, Optional
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class VideoDB:
    def __init__(self):
        self.conn_params = {
            'dbname': os.getenv('POSTGRES_DB', 'podcraftai'),
            'user': os.getenv('POSTGRES_USER', 'chiragahmedabadi'),
            'password': os.getenv('POSTGRES_PASSWORD', 'indapoint'),
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432')
        }

    def get_connection(self):
        return psycopg2.connect(**self.conn_params)

    def add_video_paths(self, job_id: int, paths: Dict[str, str] = None, video_config: Dict = None, 
                       theme: str = None, profile: str = None, customer_id: str = None) -> int:
        """
        Add video paths for a podcast job.
        
        Args:
            job_id: ID of the podcast job
            paths: Optional dictionary containing video paths with keys:
                  - audio_path
                  - welcome_audio_path
                  - intro_video_path
                  - bumper_video_path
                  - short_video_path
                  - main_video_path
                  - outro_video_path
                  - welcome_video_avatar_path
                  - hygen_short_video
            video_config: Optional dictionary containing video configuration
            theme: Optional theme name
            profile: Optional profile name
            customer_id: Optional customer identifier
            
        Returns:
            ID of the created video_paths record
        """
        paths = paths or {}
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO video_paths 
                    (job_id, audio_path, welcome_audio_path, intro_video_path,
                    bumper_video_path, short_video_path, main_video_path,
                    outro_video_path, welcome_video_avatar_path, hygen_short_video,
                    video_config, theme, profile, customer_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    job_id,
                    paths.get('audio_path'),
                    paths.get('welcome_audio_path'),
                    paths.get('intro_video_path'),
                    paths.get('bumper_video_path'),
                    paths.get('short_video_path'),
                    paths.get('main_video_path'),
                    paths.get('outro_video_path'),
                    paths.get('welcome_video_avatar_path'),
                    paths.get('hygen_short_video'),
                    json.dumps(video_config) if video_config else None,
                    theme,
                    profile,
                    customer_id
                ))
                return cursor.fetchone()[0]

    def update_video_paths(self, job_id: int, paths: Dict[str, str], video_config: Dict = None,
                          theme: str = None, profile: str = None) -> bool:
        """
        Update video paths for a podcast job.
        
        Args:
            job_id: ID of the podcast job
            paths: Dictionary containing video paths to update
            video_config: Optional dictionary containing video configuration
            theme: Optional theme name
            profile: Optional profile name
            
        Returns:
            True if update was successful, False if no record was found
        """
        update_fields = []
        values = []
        
        # Add path fields
        for key, value in paths.items():
            if value is not None:
                update_fields.append(f"{key} = %s")
                values.append(value)
                
        # Add config fields if provided
        if video_config is not None:
            update_fields.append("video_config = %s")
            values.append(json.dumps(video_config))
            
        if theme is not None:
            update_fields.append("theme = %s")
            values.append(theme)
            
        if profile is not None:
            update_fields.append("profile = %s")
            values.append(profile)
            
        if not update_fields:
            return False
            
        values.append(job_id)  # For WHERE clause
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE video_paths 
                    SET {", ".join(update_fields)}
                    WHERE job_id = %s
                """, tuple(values))
                return cursor.rowcount > 0

    def get_video_paths(self, job_id: int) -> Dict:
        """
        Get video paths for a job.
        
        Args:
            job_id: ID of the podcast job
            
        Returns:
            Dictionary containing video paths
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        intro_video_path,
                        bumper_video_path,
                        short_video_path,
                        main_video_path,
                        outro_video_path,
                        welcome_video_avatar_path
                    FROM video_paths
                    WHERE job_id = %s
                """, (job_id,))
                result = cursor.fetchone()
                
                if not result:
                    raise ValueError(f"No video paths found for job_id {job_id}")
                
                # Construct paths dictionary from individual columns and remove None values
                paths = {k: v for k, v in result.items() if v is not None}
                
                return paths

    def delete_video_paths(self, job_id: int) -> bool:
        """
        Delete video paths for a podcast job.
        
        Args:
            job_id: ID of the podcast job
        
        Returns:
            True if deletion was successful, False if no record was found
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM video_paths 
                    WHERE job_id = %s
                    RETURNING id
                """, (job_id,))
                result = cursor.fetchone()
                success = result is not None
                if success:
                    logger.info(f"Deleted video paths for job {job_id}")
                else:
                    logger.warning(f"No video paths found to delete for job {job_id}")
                return success

    def get_all_video_paths(self) -> List[Dict]:
        """
        Get all video paths records.
        
        Returns:
            List of dictionaries containing video paths
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT * FROM video_paths ORDER BY created_at DESC")
                return [dict(row) for row in cursor.fetchall()]

    def get_specific_path(self, job_id: int, path_type: str) -> Optional[str]:
        """
        Get a specific video path for a podcast job.
        
        Args:
            job_id: ID of the podcast job
            path_type: Type of path to get (e.g., 'intro_video_path', 'outro_video_path')
        
        Returns:
            Path string if found, None otherwise
        """
        valid_paths = [
            'audio_path', 'welcome_audio_path', 'intro_video_path',
            'bumper_video_path', 'short_video_path', 'main_video_path',
            'outro_video_path', 'welcome_video_avatar_path', 'hygen_short_video'
        ]
        
        if path_type not in valid_paths:
            logger.error(f"Invalid path type: {path_type}")
            return None
            
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    SELECT {path_type} FROM video_paths 
                    WHERE job_id = %s
                """, (job_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                logger.warning(f"No {path_type} found for job {job_id}")
                return None

    def add_specific_path(self, job_id: int, path_type: str, path_value: str) -> bool:
        """
        Add or update a specific video path for a podcast job.
        
        Args:
            job_id: ID of the podcast job
            path_type: Type of path to add (e.g., 'intro_video_path', 'outro_video_path')
            path_value: The path value to set
        
        Returns:
            True if successful, False otherwise
        """
        valid_paths = [
            'audio_path', 'welcome_audio_path', 'intro_video_path',
            'bumper_video_path', 'short_video_path', 'main_video_path',
            'outro_video_path', 'welcome_video_avatar_path', 'hygen_short_video'
        ]
        
        if path_type not in valid_paths:
            logger.error(f"Invalid path type: {path_type}")
            return False
            
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                # First check if a record exists for this job_id
                cursor.execute("""
                    SELECT id FROM video_paths 
                    WHERE job_id = %s
                """, (job_id,))
                
                existing_record = cursor.fetchone()
                
                if existing_record:
                    # Update existing record
                    cursor.execute(f"""
                        UPDATE video_paths 
                        SET {path_type} = %s,
                            updated_at = NOW()
                        WHERE job_id = %s
                    """, (path_value, job_id))
                else:
                    # Create new record
                    cursor.execute(f"""
                        INSERT INTO video_paths (job_id, {path_type}, created_at, updated_at)
                        VALUES (%s, %s, NOW(), NOW())
                    """, (job_id, path_value))
                
                logger.info(f"{'Updated' if existing_record else 'Added'} {path_type} for job {job_id}")
                return True

    def delete_specific_path(self, job_id: int, path_type: str) -> bool:
        """
        Set a specific video path to NULL for a podcast job.
        
        Args:
            job_id: ID of the podcast job
            path_type: Type of path to delete (e.g., 'intro_video_path', 'outro_video_path')
        
        Returns:
            True if successful, False if no record found
        """
        valid_paths = [
            'audio_path', 'welcome_audio_path', 'intro_video_path',
            'bumper_video_path', 'short_video_path', 'main_video_path',
            'outro_video_path', 'welcome_video_avatar_path', 'hygen_short_video'
        ]
        
        if path_type not in valid_paths:
            logger.error(f"Invalid path type: {path_type}")
            return False
            
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE video_paths 
                    SET {path_type} = NULL
                    WHERE job_id = %s
                    RETURNING id
                """, (job_id,))
                
                result = cursor.fetchone()
                success = result is not None
                if success:
                    logger.info(f"Deleted {path_type} for job {job_id}")
                else:
                    logger.warning(f"No video paths found for job {job_id}")
                return success

    def get_video_paths_in_order(self, job_id: int) -> dict:
        """
        Get all video paths for a job in the correct order for concatenation.
        
        Args:
            job_id: ID of the podcast job
            
        Returns:
            Dictionary with video paths in order
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        intro_video_path,
                        short_video_path,
                        bumper_video_path,
                        main_video_path,
                        outro_video_path
                    FROM video_paths 
                    WHERE job_id = %s
                """, (job_id,))
                
                result = cursor.fetchone()
                if result:
                    # Convert to regular dict and filter out None values
                    paths = dict(result)
                    return {k: v for k, v in paths.items() if v is not None}
                logger.warning(f"No video paths found for job {job_id}")
                return {}

    def add_heygen_video(self, task_id: int, heygen_video_id: str) -> int:
        """
        Add a new HeyGen video record.
        
        Args:
            task_id: ID of the podcast job task
            heygen_video_id: Video ID returned by HeyGen API
            
        Returns:
            ID of the created heygen_videos record
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO heygen_videos 
                    (task_id, heygen_video_id)
                    VALUES (%s, %s)
                    RETURNING id
                """, (task_id, heygen_video_id))
                return cursor.fetchone()[0]

    def update_heygen_video_status(self, heygen_video_id: str, status: str, video_url: str = None, 
                                 thumbnail_url: str = None, video_path: str = None, 
                                 thumbnail_path: str = None) -> bool:
        """
        Update status of a HeyGen video and optionally its URLs and paths.
        
        Args:
            heygen_video_id: Video ID from HeyGen API
            status: New status to set
            video_url: Optional video URL from HeyGen
            thumbnail_url: Optional thumbnail URL from HeyGen
            video_path: Optional local video file path
            thumbnail_path: Optional local thumbnail file path
            
        Returns:
            True if update was successful, False if no record was found
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                # Build the update query dynamically based on provided values
                update_fields = ["status = %s", "last_updated_at = CURRENT_TIMESTAMP"]
                params = [status]
                
                if video_url is not None:
                    update_fields.append("video_url = %s")
                    params.append(video_url)
                if thumbnail_url is not None:
                    update_fields.append("thumbnail_url = %s")
                    params.append(thumbnail_url)
                if video_path is not None:
                    update_fields.append("video_path = %s")
                    params.append(video_path)
                if thumbnail_path is not None:
                    update_fields.append("thumbnail_path = %s")
                    params.append(thumbnail_path)
                    
                query = f"""
                    UPDATE heygen_videos 
                    SET {", ".join(update_fields)}
                    WHERE heygen_video_id = %s
                    RETURNING id
                """
                params.append(heygen_video_id)
                
                cursor.execute(query, params)
                return cursor.fetchone() is not None

    def get_heygen_video_status(self, job_id: int) -> dict:
        """
        Get HeyGen video status and path for a job.
        
        Args:
            job_id: The job ID to check
            
        Returns:
            dict: Contains status and video_path if found, None if no record exists
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT h.status, h.video_path
                        FROM heygen_videos h
                        WHERE h.task_id = %s
                        ORDER BY h.created_at DESC
                        LIMIT 1
                    """, (job_id,))
                    
                    result = cursor.fetchone()
                    if result:
                        return {
                            'status': result[0],
                            'video_path': result[1]
                        }
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting heygen video status: {str(e)}")
            return None

    def get_heygen_video_status_and_paths(self, task_id: int = None, heygen_video_id: str = None) -> Dict:
        """
        Get status of a HeyGen video by either task_id or heygen_video_id.
        
        Args:
            task_id: Optional task ID to lookup
            heygen_video_id: Optional HeyGen video ID to lookup
            
        Returns:
            Dictionary containing video status info or None if not found
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                if task_id:
                    cursor.execute("""
                        SELECT task_id, heygen_video_id, status,video_path, thumbnail_path, created_at, last_updated_at
                        FROM heygen_videos
                        WHERE task_id = %s
                    """, (task_id,))
                else:
                    cursor.execute("""
                        SELECT task_id, heygen_video_id, status, video_path, thumbnail_path, created_at, last_updated_at
                        FROM heygen_videos
                        WHERE heygen_video_id = %s
                    """, (heygen_video_id,))
                    
                result = cursor.fetchone()
                if result:
                    return {
                        'task_id': result[0],
                        'heygen_video_id': result[1],
                        'status': result[2],
                        'video_path': result[3],
                        'thumbnail_path': result[4],
                        'created_at': result[5],
                        'last_updated_at': result[6]
                    }
                return None

    def update_video_config(self, job_id: int, config: Dict) -> bool:
        """
        Update video configuration for a podcast job.
        
        Args:
            job_id: ID of the podcast job
            config: Dictionary containing video configuration
            
        Returns:
            True if update was successful, False if no record was found
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE video_paths 
                    SET video_config = %s
                    WHERE job_id = %s
                    RETURNING id
                """, (json.dumps(config), job_id))
                return cursor.rowcount > 0

    def update_video_theme(self, job_id: int, theme: str) -> bool:
        """
        Update video theme for a podcast job.
        
        Args:
            job_id: ID of the podcast job
            theme: Theme name to set
            
        Returns:
            True if update was successful, False if no record was found
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE video_paths 
                    SET theme = %s
                    WHERE job_id = %s
                    RETURNING id
                """, (theme, job_id))
                return cursor.rowcount > 0

    def update_video_profile(self, job_id: int, profile: str) -> bool:
        """
        Update video profile for a podcast job.
        
        Args:
            job_id: ID of the podcast job
            profile: Profile name to set
            
        Returns:
            True if update was successful, False if no record was found
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE video_paths 
                    SET profile = %s
                    WHERE job_id = %s
                    RETURNING id
                """, (profile, job_id))
                return cursor.rowcount > 0

    def get_video_config(self, job_id: int) -> Dict:
        """
        Get video configuration details for a job.
        
        Args:
            job_id: ID of the podcast job
            
        Returns:
            Dictionary containing video configuration:
            {
                'video_config': {
                    'fps': 30,
                    'video_codec': 'libx264',
                    'video_bitrate': '8000k',
                    'audio_codec': 'aac',
                    'audio_bitrate': '128k',
                    'resolution': (1280, 720)
                }
            }
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        video_config,
                        theme,
                        profile
                    FROM video_paths
                    WHERE job_id = %s
                """, (job_id,))
                result = cursor.fetchone()
                
                if not result:
                    raise ValueError(f"No configuration found for job_id {job_id}")
                
                # Default video settings
                config = {
                    'video_config': {
                        'fps': 30,
                        'video_codec': 'libx264',
                        'video_bitrate': '8000k',
                        'audio_codec': 'aac',
                        'audio_bitrate': '128k',
                        'resolution': (1280, 720)
                    }
                }
                
                # Update with stored video settings
                if result['video_config']:
                    config['video_config'].update(result['video_config'])
                
                config['theme'] = result['theme']
                config['profile'] = result['profile']
                
                return config

    def update_video_status(self, job_id: int, status: str, final_video_path: str = None, 
                          error_details: str = None) -> bool:
        """
        Update video status and optionally the final video path and error details.
        
        Args:
            job_id: ID of the podcast job
            status: New status to set (e.g., pending, processing, completed, failed)
            final_video_path: Optional path to the final video file
            error_details: Optional error message if status is 'failed'
            
        Returns:
            True if update was successful, False if no record was found
        """
        update_fields = ["status = %s"]
        values = [status]
        
        if final_video_path is not None:
            update_fields.append("final_video_path = %s")
            values.append(final_video_path)
            
        if error_details is not None:
            update_fields.append("error_details = %s")
            values.append(error_details)
            
        values.append(job_id)  # For WHERE clause
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE video_paths 
                    SET {", ".join(update_fields)}
                    WHERE job_id = %s
                    RETURNING id
                """, tuple(values))
                return cursor.rowcount > 0

    def get_video_status(self, job_id: int) -> Optional[Dict]:
        """
        Get video status and tracking information.
        
        Args:
            job_id: ID of the podcast job
            
        Returns:
            Dictionary containing status, final_video_path, retry_count, error_details,
            created_at, and updated_at or None if not found
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        status, 
                        final_video_path,
                        retry_count,
                        error_details,
                        created_at,
                        updated_at
                    FROM video_paths 
                    WHERE job_id = %s
                """, (job_id,))
                result = cursor.fetchone()
                if result:
                    return dict(result)
                return None

    def get_failed_videos(self, max_retries: int = 3) -> List[Dict]:
        """
        Get list of failed videos that haven't exceeded max retry count.
        
        Args:
            max_retries: Maximum number of retries allowed
            
        Returns:
            List of dictionaries containing video information
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        job_id,
                        status,
                        retry_count,
                        error_details,
                        created_at,
                        updated_at
                    FROM video_paths 
                    WHERE status = 'failed'
                    AND retry_count < %s
                    ORDER BY updated_at DESC
                """, (max_retries,))
                return [dict(row) for row in cursor.fetchall()]

    def get_pending_videos(self, max_retries: int = 5) -> List[Dict]:
        """
        Get list of videos that need processing:
        - Status is pending OR
        - Final video path is blank
        - Status is not error
        - Retry count is less than max_retries
        
        Args:
            max_retries: Maximum number of retries allowed
            
        Returns:
            List of dictionaries containing video information
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT v.*,
                    j.topic,
                    j.profile_name,
                    j.customer_id
                    FROM video_paths v
                    JOIN podcast_jobs j ON v.job_id = j.id
                    WHERE (v.status = 'pending' 
                          OR (v.final_video_path IS NULL AND v.status != 'error'))
                    AND v.retry_count < %s
                    ORDER BY v.created_at ASC
                """, (max_retries,))
                return [dict(row) for row in cursor.fetchall()]

    def update_heygen_video_flag(self, job_id: int, is_heygen_video: bool = True) -> bool:
        """
        Update is_heygen_video flag for a specific job.
        
        Args:
            job_id: The job ID to update
            is_heygen_video: Boolean flag to set (default True)
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE video_paths
                        SET is_heygen_video = %s
                        WHERE job_id = %s
                        RETURNING id
                    """, (is_heygen_video, job_id))
                    
                    result = cursor.fetchone()
                    conn.commit()
                    
                    return result is not None
                    
        except Exception as e:
            logger.error(f"Error updating heygen video flag: {str(e)}")
            return False

    def get_pending_youtube_uploads(self) -> List[Dict]:
        """
        Get list of videos pending YouTube upload.
        
        Returns:
            List of dictionaries containing video information
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT yv.*, vp.final_video_path, pj.title as job_title, 
                           pj.description as job_description,
                           yc.channel_id, yc.credentials_path, yc.token_path,
                           yp.playlist_id
                    FROM youtube_videos yv
                    JOIN video_paths vp ON yv.video_path_id = vp.id
                    JOIN podcast_jobs pj ON yv.job_id = pj.id
                    JOIN youtube_channels yc ON yv.channel_id = yc.id
                    LEFT JOIN youtube_playlists yp ON yv.playlist_id = yp.id
                    WHERE yv.status = 'pending'
                    AND vp.final_video_path IS NOT NULL
                    ORDER BY yv.id ASC
                """)
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def create_youtube_channel(self, customer_id: str, channel_id: str, channel_title: str,
                             credentials_path: str, token_path: str) -> int:
        """
        Create a new YouTube channel configuration.
        
        Args:
            customer_id: Customer ID
            channel_id: YouTube channel ID
            channel_title: Channel title
            credentials_path: Path to credentials file
            token_path: Path to token file
            
        Returns:
            ID of created channel record
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO youtube_channels
                    (customer_id, channel_id, channel_title, credentials_path, token_path)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (customer_id, channel_id, channel_title, credentials_path, token_path))
                return cursor.fetchone()[0]

    def get_youtube_channel(self, customer_id: str, channel_id: str) -> Optional[Dict]:
        """
        Get YouTube channel configuration.
        
        Args:
            customer_id: Customer ID
            channel_id: YouTube channel ID
            
        Returns:
            Dictionary containing channel configuration or None if not found
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT *
                    FROM youtube_channels
                    WHERE customer_id = %s AND channel_id = %s
                """, (customer_id, channel_id))
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
                return None

    def get_youtube_playlist(self, channel_id: int, playlist_id: str) -> Optional[Dict]:
        """
        Get YouTube playlist information.
        
        Args:
            channel_id: Channel ID from youtube_channels table
            playlist_id: YouTube playlist ID
            
        Returns:
            Dictionary containing playlist information or None if not found
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT *
                    FROM youtube_playlists
                    WHERE channel_id = %s AND playlist_id = %s
                """, (channel_id, playlist_id))
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
                return None

    def create_youtube_playlist(self, channel_id: int, playlist_id: str, 
                              playlist_title: str) -> int:
        """
        Create a new YouTube playlist record.
        
        Args:
            channel_id: Channel ID from youtube_channels table
            playlist_id: YouTube playlist ID
            playlist_title: Playlist title
            
        Returns:
            ID of created playlist record
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO youtube_playlists
                    (channel_id, playlist_id, playlist_title)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (channel_id, playlist_id, playlist_title))
                return cursor.fetchone()[0]

    def create_youtube_video(self, job_id: int, customer_id: str, channel_id: int,
                           playlist_id: int = None, video_path_id: int = None,
                           title: str = None, description: str = None,
                           tags: List[str] = None, privacy_status: str = 'private') -> int:
        """
        Create a new YouTube video record.
        
        Args:
            job_id: Podcast job ID
            customer_id: Customer ID
            channel_id: Channel ID from youtube_channels table
            playlist_id: Optional playlist ID from youtube_playlists table
            video_path_id: Optional video path ID from video_paths table
            title: Optional video title
            description: Optional video description
            tags: Optional list of video tags
            privacy_status: Video privacy status (private/public/unlisted)
            
        Returns:
            ID of created video record
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO youtube_videos
                    (job_id, customer_id, channel_id, playlist_id, video_path_id,
                     title, description, tags, privacy_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (job_id, customer_id, channel_id, playlist_id, video_path_id,
                      title, description, tags, privacy_status))
                return cursor.fetchone()[0]

    def update_youtube_video_status(self, video_id: int, status: str,
                                  youtube_video_id: str = None,
                                  error_message: str = None) -> None:
        """
        Update YouTube video upload status.
        
        Args:
            video_id: ID from youtube_videos table
            status: New status (uploaded/error)
            youtube_video_id: Optional YouTube video ID
            error_message: Optional error message if status is 'error'
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE youtube_videos
                    SET status = %s,
                        youtube_video_id = %s,
                        error_message = %s,
                        upload_date = CASE 
                            WHEN %s = 'uploaded' THEN NOW()
                            ELSE upload_date
                        END
                    WHERE id = %s
                """, (status, youtube_video_id, error_message, status, video_id))

    def update_youtube_status(self, job_id: int, status: str, youtube_id: str = None,
                            error_message: str = None) -> None:
        """
        Update YouTube upload status for a video.
        
        Args:
            job_id: ID of the podcast job
            status: New status (uploaded/error)
            youtube_id: Optional YouTube video ID
            error_message: Optional error message if status is 'error'
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE video_paths
                    SET youtube_status = %s,
                        youtube_id = %s,
                        youtube_error = %s,
                        youtube_upload_date = CASE 
                            WHEN %s = 'uploaded' THEN NOW()
                            ELSE youtube_upload_date
                        END
                    WHERE job_id = %s
                """, (status, youtube_id, error_message, status, job_id))
