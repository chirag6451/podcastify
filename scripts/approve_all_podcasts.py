import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create a database connection."""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'podcraftai'),
        user=os.getenv('POSTGRES_USER', 'chiragahmedabadi'),
        password=os.getenv('POSTGRES_PASSWORD', 'indapoint')
    )

def approve_all_podcasts():
    """Update all podcast audio records to approved status."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Update all records to approved status
        update_query = """
        UPDATE podcast_audio_details 
        SET 
            approval_status = 'approved',
            approved_by = 'admin',
            approved_at = CURRENT_TIMESTAMP
        WHERE approval_status IS NULL 
        OR approval_status != 'approved'
        RETURNING id, job_id, approval_status, approved_at;
        """
        
        cur.execute(update_query)
        updated_records = cur.fetchall()
        
        # Commit the changes
        conn.commit()
        
        # Print results
        print(f"\nUpdated {len(updated_records)} records to approved status:")
        for record in updated_records:
            print(f"ID: {record[0]}, Job ID: {record[1]}, Status: {record[2]}, Approved At: {record[3]}")
            
    except Exception as e:
        print(f"Error updating records: {str(e)}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    approve_all_podcasts()
