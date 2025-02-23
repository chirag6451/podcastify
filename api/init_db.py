import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

load_dotenv()

def init_database():
    # Database configuration
    POSTGRES_USER = os.getenv("POSTGRES_USER", "chiragahmedabadi")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "indapoint")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "podcraftai")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

    try:
        # Connect to default PostgreSQL database first
        conn = psycopg2.connect(
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database="postgres"  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{POSTGRES_DB}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database {POSTGRES_DB}...")
            cursor.execute(f'CREATE DATABASE {POSTGRES_DB}')
            print(f"Database {POSTGRES_DB} created successfully!")
        else:
            print(f"Database {POSTGRES_DB} already exists.")

        cursor.close()
        conn.close()

        # Now create tables using SQLAlchemy
        from api.models import Base, engine
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print("Database initialization completed!")
