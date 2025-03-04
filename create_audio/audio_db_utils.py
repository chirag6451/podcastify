"""Module for managing podcast audio details in the database."""
import json
from datetime import datetime
from typing import Dict, Optional
import psycopg2
from psycopg2.extras import Json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AudioDBManger:
    def __init__(self):
        """Initialize database connection."""
        db_params = {
            'dbname': os.getenv('POSTGRES_DB', 'podcraftai'),
            'user': os.getenv('POSTGRES_USER', 'chiragahmedabadi'),
            'password': os.getenv('POSTGRES_PASSWORD', 'indapoint'),
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432')
        }
        self.conn = psycopg2.connect(**db_params)
        self.cur = self.conn.cursor()

    def create_audio_record(
        self,
        job_id: str,
        customer_id: str,
        welcome_voiceover_text: Optional[str] = None,
        conversation_data: Optional[Dict] = None,
        intro_voiceover_text: Optional[str] = None,
        podcast_intro_voiceover: Optional[str] = None,
        default_podcast_intro_text: Optional[str] = None,
        voice_settings: Optional[Dict] = None,
        request_data: Optional[Dict] = None,
        welcome_audio_path: Optional[str] = None,
        conversation_audio_path: Optional[str] = None,
        intro_audio_path: Optional[str] = None,
        podcast_intro_audio_path: Optional[str] = None,
        default_podcast_intro_audio_path: Optional[str] = None,
        final_mix_path: Optional[str] = None,
        schema_path: Optional[str] = None
    ) -> int:
        """Create a new audio record."""
        query = """
        INSERT INTO podcast_audio_details (
            job_id,
            customer_id,
            welcome_voiceover_text,
            conversation_data,
            intro_voiceover_text,
            podcast_intro_voiceover,
            default_podcast_intro_text,
            voice_settings,
            request_data,
            welcome_audio_path,
            conversation_audio_path,
            intro_audio_path,
            podcast_intro_audio_path,
            default_podcast_intro_audio_path,
            final_mix_path,
            schema_path,
            status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
        RETURNING id;
        """
        
        self.cur.execute(query, (
            job_id,
            customer_id,
            welcome_voiceover_text,
            Json(conversation_data) if conversation_data else None,
            intro_voiceover_text,
            podcast_intro_voiceover,
            default_podcast_intro_text,
            Json(voice_settings) if voice_settings else None,
            Json(request_data) if request_data else None,
            welcome_audio_path,
            Json(conversation_audio_path) if conversation_audio_path else None,  # Since this might be a dict of paths
            intro_audio_path,
            podcast_intro_audio_path,
            default_podcast_intro_audio_path,
            final_mix_path,
            schema_path
        ))
        record_id = self.cur.fetchone()[0]
        self.conn.commit()
        return record_id

    def update_audio_paths(
        self,
        job_id: str,
        welcome_audio_path: Optional[str] = None,
        conversation_audio_path: Optional[str] = None,
        intro_audio_path: Optional[str] = None,
        podcast_intro_audio_path: Optional[str] = None,
        default_podcast_intro_audio_path: Optional[str] = None,
        final_mix_path: Optional[str] = None,
        schema_path: Optional[str] = None
    ) -> bool:
        """Update audio file paths for a job."""
        query = """
        UPDATE podcast_audio_details
        SET 
            welcome_audio_path = COALESCE(%s, welcome_audio_path),
            conversation_audio_path = COALESCE(%s, conversation_audio_path),
            intro_audio_path = COALESCE(%s, intro_audio_path),
            podcast_intro_audio_path = COALESCE(%s, podcast_intro_audio_path),
            default_podcast_intro_audio_path = COALESCE(%s, default_podcast_intro_audio_path),
            final_mix_path = COALESCE(%s, final_mix_path),
            schema_path = COALESCE(%s, schema_path),
            updated_at = CURRENT_TIMESTAMP
        WHERE job_id = %s
        RETURNING id;
        """
        
        self.cur.execute(query, (
            welcome_audio_path,
            conversation_audio_path,
            intro_audio_path,
            podcast_intro_audio_path,
            default_podcast_intro_audio_path,
            final_mix_path,
            schema_path,
            job_id
        ))
        success = self.cur.rowcount > 0
        self.conn.commit()
        return success

    def update_transistor_details(
        self,
        job_id: str,
        episode_id: Optional[str] = None,
        show_id: Optional[str] = None,
        audio_url: Optional[str] = None
    ) -> bool:
        """Update Transistor.fm details for a job."""
        query = """
        UPDATE podcast_audio_details
        SET 
            transistor_episode_id = COALESCE(%s, transistor_episode_id),
            transistor_show_id = COALESCE(%s, transistor_show_id),
            transistor_audio_url = COALESCE(%s, transistor_audio_url),
            updated_at = CURRENT_TIMESTAMP
        WHERE job_id = %s
        RETURNING id;
        """
        
        self.cur.execute(query, (
            episode_id,
            show_id,
            audio_url,
            job_id
        ))
        success = self.cur.rowcount > 0
        self.conn.commit()
        return success

    def update_status(
        self,
        job_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """Update job status and optional error message."""
        query = """
        UPDATE podcast_audio_details
        SET 
            status = %s,
            error_message = %s,
            completed_at = CASE 
                WHEN %s IN ('completed', 'failed') THEN CURRENT_TIMESTAMP 
                ELSE completed_at 
            END,
            updated_at = CURRENT_TIMESTAMP
        WHERE job_id = %s
        RETURNING id;
        """
        
        self.cur.execute(query, (
            status,
            error_message,
            status,
            job_id
        ))
        success = self.cur.rowcount > 0
        self.conn.commit()
        return success

    def get_audio_details(self, job_id: str) -> Optional[Dict]:
        """Get all details for a job."""
        query = """
        SELECT 
            id,
            job_id,
            customer_id,
            welcome_voiceover_text,
            conversation_data,
            intro_voiceover_text,
            podcast_intro_voiceover,
            welcome_audio_path,
            conversation_audio_path,
            intro_audio_path,
            podcast_intro_audio_path,
            default_podcast_intro_audio_path,
            final_mix_path,
            schema_path,
            transistor_episode_id,
            transistor_show_id,
            transistor_audio_url,
            status,
            error_message,
            voice_settings,
            request_data,
            default_podcast_intro_text,
            created_at,
            updated_at,
            completed_at
        FROM podcast_audio_details
        WHERE job_id = %s;
        """
        
        self.cur.execute(query, (job_id,))
        row = self.cur.fetchone()
        
        if not row:
            return None
            
        # Convert to dictionary
        columns = [desc[0] for desc in self.cur.description]
        result = dict(zip(columns, row))
        
        # Parse JSON fields
        for json_field in ['conversation_data', 'voice_settings', 'request_data']:
            if result[json_field]:
                result[json_field] = json.loads(result[json_field])
                
        return result

    def submit_for_approval(
        self,
        job_id: str,
        submitted_by: str,
        comments: Optional[str] = None
    ) -> bool:
        """Submit an audio record for approval."""
        query = """
        UPDATE podcast_audio_details
        SET 
            approval_status = 'pending_approval',
            last_modified_by = %s,
            approval_comments = CASE 
                WHEN %s IS NOT NULL THEN %s 
                ELSE approval_comments 
            END,
            submitted_for_approval_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE job_id = %s AND approval_status = 'draft'
        RETURNING id;
        """
        
        self.cur.execute(query, (
            submitted_by,
            comments,
            comments,
            job_id
        ))
        success = self.cur.rowcount > 0
        self.conn.commit()
        return success

    def approve_audio(
        self,
        job_id: str,
        approved_by: str,
        comments: Optional[str] = None
    ) -> bool:
        """Approve an audio record."""
        query = """
        UPDATE podcast_audio_details
        SET 
            approval_status = 'approved',
            approved_by = %s,
            approved_at = CURRENT_TIMESTAMP,
            last_modified_by = %s,
            approval_comments = CASE 
                WHEN %s IS NOT NULL THEN %s 
                ELSE approval_comments 
            END,
            approved_version = COALESCE(approved_version, 1),
            updated_at = CURRENT_TIMESTAMP
        WHERE job_id = %s AND approval_status = 'pending_approval'
        RETURNING id;
        """
        
        self.cur.execute(query, (
            approved_by,
            approved_by,
            comments,
            comments,
            job_id
        ))
        success = self.cur.rowcount > 0
        self.conn.commit()
        return success

    def reject_audio(
        self,
        job_id: str,
        rejected_by: str,
        rejection_reason: str,
        comments: Optional[str] = None
    ) -> bool:
        """Reject an audio record."""
        query = """
        UPDATE podcast_audio_details
        SET 
            approval_status = 'rejected',
            last_modified_by = %s,
            rejected_at = CURRENT_TIMESTAMP,
            rejection_reason = %s,
            approval_comments = CASE 
                WHEN %s IS NOT NULL THEN %s 
                ELSE approval_comments 
            END,
            updated_at = CURRENT_TIMESTAMP
        WHERE job_id = %s AND approval_status = 'pending_approval'
        RETURNING id;
        """
        
        self.cur.execute(query, (
            rejected_by,
            rejection_reason,
            comments,
            comments,
            job_id
        ))
        success = self.cur.rowcount > 0
        self.conn.commit()
        return success

    def get_approval_status(self, job_id: str) -> Optional[Dict]:
        """Get approval status and details for a job."""
        query = """
        SELECT 
            approval_status,
            approved_by,
            approved_at,
            rejected_at,
            rejection_reason,
            approved_version,
            approval_comments,
            last_modified_by,
            submitted_for_approval_at
        FROM podcast_audio_details
        WHERE job_id = %s;
        """
        
        self.cur.execute(query, (job_id,))
        row = self.cur.fetchone()
        
        if not row:
            return None
            
        columns = [
            'approval_status',
            'approved_by',
            'approved_at',
            'rejected_at',
            'rejection_reason',
            'approved_version',
            'approval_comments',
            'last_modified_by',
            'submitted_for_approval_at'
        ]
        return dict(zip(columns, row))

    def __del__(self):
        """Close database connection."""
        if hasattr(self, 'cur'):
            self.cur.close()
        if hasattr(self, 'conn'):
            self.conn.commit()
            self.conn.close()
