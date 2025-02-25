import psycopg2
from psycopg2.extras import Json
import os

def get_postgres_connection():
    return psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB', 'podcraftai'),
        user=os.getenv('POSTGRES_USER', 'chiragahmedabadi'),
        password=os.getenv('POSTGRES_PASSWORD', 'indapoint'),
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432')
    )

def add_sample_data():
    # Sample voice data
    voices = [
        {
            'voice_id': 'adam',
            'name': 'Adam',
            'category': 'professional',
            'description': 'Professional male voice with American accent',
            'labels': {'tone': 'professional', 'clarity': 'high'},
            'gender': 'male',
            'accent': 'American',
            'age': 'adult',
            'language': 'english',
            'use_case': 'business',
            'preview_url': '',
            'settings': {'stability': 0.5, 'similarity_boost': 0.75}
        },
        {
            'voice_id': 'sarah',
            'name': 'Sarah',
            'category': 'professional',
            'description': 'Professional female voice with American accent',
            'labels': {'tone': 'professional', 'clarity': 'high'},
            'gender': 'female',
            'accent': 'American',
            'age': 'adult',
            'language': 'english',
            'use_case': 'business',
            'preview_url': '',
            'settings': {'stability': 0.5, 'similarity_boost': 0.75}
        }
    ]

    # Sample speaker profiles
    profiles = [
        {
            'speaker_id': 'host_adam',
            'name': 'Host Adam',
            'voice_id': 'adam',
            'gender': 'male',
            'personality': {
                'traits': ['professional', 'engaging', 'knowledgeable'],
                'style': 'conversational'
            },
            'ideal_for': {
                'topics': ['business', 'technology', 'science'],
                'roles': ['host', 'interviewer']
            },
            'accent': 'American',
            'best_languages': ['english']
        },
        {
            'speaker_id': 'host_sarah',
            'name': 'Host Sarah',
            'voice_id': 'sarah',
            'gender': 'female',
            'personality': {
                'traits': ['professional', 'warm', 'articulate'],
                'style': 'engaging'
            },
            'ideal_for': {
                'topics': ['business', 'leadership', 'innovation'],
                'roles': ['host', 'moderator']
            },
            'accent': 'American',
            'best_languages': ['english']
        }
    ]

    conn = get_postgres_connection()
    cur = conn.cursor()

    try:
        # Add voices
        print("Adding sample voices...")
        for voice in voices:
            cur.execute("""
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
                voice['voice_id'],
                voice['name'],
                voice['category'],
                voice['description'],
                Json(voice['labels']),
                voice['gender'],
                voice['accent'],
                voice['age'],
                voice['language'],
                voice['use_case'],
                voice['preview_url'],
                Json(voice['settings'])
            ))

        # Add speaker profiles
        print("Adding sample speaker profiles...")
        for profile in profiles:
            cur.execute("""
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
                profile['speaker_id'],
                profile['name'],
                profile['voice_id'],
                profile['gender'],
                Json(profile['personality']),
                Json(profile['ideal_for']),
                profile['accent'],
                Json(profile['best_languages'])
            ))

        # Commit the changes
        conn.commit()
        print("Sample data added successfully!")

    except Exception as e:
        print(f"Error adding sample data: {str(e)}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    add_sample_data()
