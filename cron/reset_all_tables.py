#!/usr/bin/env python3
import os
import sys
import logging
import psycopg2
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

def reset_all_tables():
    """Reset all tables with cascade delete."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # List of tables to clear in order of dependencies
        tables = [
            'youtube_video_metadata',
            'youtube_video_templates',
            'heygen_videos',
            'user_drive_uploads',
            'video_paths',
            'podcast_jobs'
        ]

        # Get count before deletion
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            logger.info(f"Current count in {table}: {count}")

        # Disable triggers temporarily
        cur.execute("SET session_replication_role = 'replica';")

        # Delete from each table
        for table in tables:
            cur.execute(f"TRUNCATE TABLE {table} CASCADE;")
            logger.info(f"Cleared table: {table}")

        # Re-enable triggers
        cur.execute("SET session_replication_role = 'origin';")

        # Verify counts after deletion
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            logger.info(f"New count in {table}: {count}")

        conn.commit()
        logger.info("Successfully reset all tables")

    except Exception as e:
        logger.error(f"Error resetting tables: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    # Add confirmation prompt
    response = input("This will delete ALL data from the tables. Are you sure? (yes/no): ")
    if response.lower() == 'yes':
        reset_all_tables()
    else:
        logger.info("Operation cancelled")
