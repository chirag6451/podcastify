#!/usr/bin/env python3
import os
import sys
import logging
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s %(levelname)-8s %(message)s',
                   datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create a database connection."""
    load_dotenv()
    return psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT')
    )

def reset_youtube_process():
    """Reset all tables related to YouTube upload process."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get a list of completed jobs
        cur.execute("""
            SELECT id FROM podcast_jobs 
            WHERE status = 'completed' 
            ORDER BY id DESC 
            LIMIT 5
        """)
        job_ids = [row[0] for row in cur.fetchall()]

        if not job_ids:
            logger.info("No completed jobs found to reset")
            return

        job_ids_str = ','.join(str(id) for id in job_ids)
        logger.info(f"Resetting process for job IDs: {job_ids_str}")

        # Delete existing YouTube metadata
        cur.execute(f"""
            DELETE FROM youtube_video_metadata 
            WHERE job_id IN ({job_ids_str})
        """)
        logger.info("Reset youtube_video_metadata table")

        # Reset video_paths status
        cur.execute(f"""
            UPDATE video_paths 
            SET status = 'completed'
            WHERE job_id IN ({job_ids_str})
        """)
        logger.info("Reset video_paths status")

        # Commit the changes
        conn.commit()
        logger.info("Successfully reset all tables")

        # Show current state
        cur.execute(f"""
            SELECT 
                j.id as job_id,
                j.status as job_status,
                vp.status as video_path_status,
                vp.final_video_path,
                yvm.publish_status as youtube_status
            FROM podcast_jobs j
            LEFT JOIN video_paths vp ON vp.job_id = j.id
            LEFT JOIN youtube_video_metadata yvm ON yvm.job_id = j.id
            WHERE j.id IN ({job_ids_str})
            ORDER BY j.id;
        """)
        
        logger.info("\nCurrent state after reset:")
        logger.info("JobID | Job Status | Video Status | YouTube Status | Video Path")
        logger.info("-" * 100)
        for row in cur.fetchall():
            logger.info(f"{row[0]} | {row[1]} | {row[2]} | {row[4]} | {row[3]}")

    except Exception as e:
        logger.error(f"Error resetting process: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    reset_youtube_process()
