import sqlite3
import psycopg2
from psycopg2.extras import Json
import json
import os

def get_postgres_connection():
    return psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB', 'podcraftai'),
        user=os.getenv('POSTGRES_USER', 'chiragahmedabadi'),
        password=os.getenv('POSTGRES_PASSWORD', 'indapoint'),
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432')
    )

def migrate_data():
    # Connect to SQLite database
    sqlite_conn = sqlite3.connect('podcast.db')
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    # Connect to PostgreSQL database
    pg_conn = get_postgres_connection()
    pg_cur = pg_conn.cursor()

    try:
        # Migrate elevenlabs_voices
        print("Migrating elevenlabs_voices...")
        sqlite_cur.execute("SELECT * FROM elevenlabs_voices")
        voices = sqlite_cur.fetchall()
        
        for voice in voices:
            voice_dict = dict(voice)
            # Convert JSON strings to dicts for PostgreSQL JSONB
            try:
                labels = json.loads(voice_dict['labels']) if voice_dict['labels'] else {}
            except:
                labels = {}
                
            try:
                settings = json.loads(voice_dict['settings']) if voice_dict['settings'] else {}
            except:
                settings = {}

            pg_cur.execute("""
                INSERT INTO elevenlabs_voices 
                (voice_id, name, category, description, labels, gender, 
                 accent, age, language, use_case, preview_url, settings)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (voice_id) DO UPDATE SET
                name = EXCLUDED.name,
                category = EXCLUDED.category,
                description = EXCLUDED.description,
                labels = EXCLUDED.labels,
                gender = EXCLUDED.gender,
                accent = EXCLUDED.accent,
                age = EXCLUDED.age,
                language = EXCLUDED.language,
                use_case = EXCLUDED.use_case,
                preview_url = EXCLUDED.preview_url,
                settings = EXCLUDED.settings
            """, (
                voice_dict['voice_id'],
                voice_dict['name'],
                voice_dict['category'],
                voice_dict['description'],
                Json(labels),
                voice_dict['gender'],
                voice_dict['accent'],
                voice_dict['age'],
                voice_dict['language'],
                voice_dict['use_case'],
                voice_dict['preview_url'],
                Json(settings)
            ))

        # Migrate speaker_profiles
        print("Migrating speaker_profiles...")
        sqlite_cur.execute("SELECT * FROM speaker_profiles")
        profiles = sqlite_cur.fetchall()
        
        for profile in profiles:
            profile_dict = dict(profile)
            # Convert JSON strings to dicts for PostgreSQL JSONB
            try:
                personality = json.loads(profile_dict['personality']) if profile_dict['personality'] else {}
            except:
                personality = {}
                
            try:
                ideal_for = json.loads(profile_dict['ideal_for']) if profile_dict['ideal_for'] else {}
            except:
                ideal_for = {}
                
            try:
                best_languages = json.loads(profile_dict['best_languages']) if profile_dict['best_languages'] else []
            except:
                best_languages = []

            pg_cur.execute("""
                INSERT INTO speaker_profiles 
                (speaker_id, name, voice_id, gender, personality, 
                 ideal_for, accent, best_languages)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (speaker_id) DO UPDATE SET
                name = EXCLUDED.name,
                voice_id = EXCLUDED.voice_id,
                gender = EXCLUDED.gender,
                personality = EXCLUDED.personality,
                ideal_for = EXCLUDED.ideal_for,
                accent = EXCLUDED.accent,
                best_languages = EXCLUDED.best_languages
            """, (
                profile_dict['speaker_id'],
                profile_dict['name'],
                profile_dict['voice_id'],
                profile_dict['gender'],
                Json(personality),
                Json(ideal_for),
                profile_dict['accent'],
                Json(best_languages)
            ))

        # Commit the changes
        pg_conn.commit()
        print("Migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {str(e)}")
        pg_conn.rollback()
    finally:
        sqlite_cur.close()
        sqlite_conn.close()
        pg_cur.close()
        pg_conn.close()

if __name__ == "__main__":
    migrate_data()
