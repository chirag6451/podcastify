import psycopg2
from psycopg2.extras import Json
from typing import Dict, List, Optional
import json
from create_audio.openai_utils import GetBestVoiceID
import logging
import os

logger = logging.getLogger(__name__)

class PodcastDB:
    def __init__(self):
        self.conn_params = {
            'dbname': os.getenv('POSTGRES_DB', 'podcraftai'),
            'user': os.getenv('POSTGRES_USER', 'chiragahmedabadi'),
            'password': os.getenv('POSTGRES_PASSWORD', 'indapoint'),
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432')
        }
        self.init_db()

    def get_connection(self):
        return psycopg2.connect(**self.conn_params)

    def init_db(self):
        # Tables are already created via SQL migration
        pass

    def add_elevenlabs_voice(self, voice_data: Dict):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
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
                    voice_data['voice_id'],
                    voice_data.get('name'),
                    voice_data.get('category'),
                    voice_data.get('description'),
                    Json(voice_data.get('labels', {})),
                    voice_data.get('gender'),
                    voice_data.get('accent'),
                    voice_data.get('age'),
                    voice_data.get('language'),
                    voice_data.get('use_case'),
                    voice_data.get('preview_url'),
                    Json(voice_data.get('settings', {}))
                ))

    def add_speaker_profile(self, profile_data: Dict):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
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
                    profile_data['speaker_id'],
                    profile_data.get('name'),
                    profile_data.get('voice_id'),
                    profile_data.get('gender'),
                    Json(profile_data.get('personality', {})),
                    Json(profile_data.get('ideal_for', {})),
                    profile_data.get('accent'),
                    Json(profile_data.get('best_languages', []))
                ))

    def get_elevenlabs_voices(self) -> List[Dict]:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM elevenlabs_voices")
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_speaker_profiles(self) -> List[Dict]:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM speaker_profiles")
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def search_elevenlabs_voices(self, 
                               gender: Optional[str] = None,
                               accent: Optional[str] = None,
                               language: Optional[str] = None,
                               category: Optional[str] = None) -> List[Dict]:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT * FROM elevenlabs_voices WHERE 1=1"
                params = []
                
                if gender:
                    query += " AND gender = %s"
                    params.append(gender)
                if accent:
                    query += " AND accent = %s"
                    params.append(accent)
                if language:
                    query += " AND language = %s"
                    params.append(language)
                if category:
                    query += " AND category = %s"
                    params.append(category)
                
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                return [self._process_elevenlabs_row(dict(zip(columns, row))) for row in rows]

    def get_voice_records(self, limit: int = 30) -> List[Dict]:
        """
        Get all voice records from database with specified limit.
        
        Args:
            limit: Maximum number of records to return (default: 30)
            
        Returns:
            List of dictionaries containing voice details
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT speaker_id, voice_id, name, gender, personality, ideal_for, accent, best_languages
                FROM speaker_profiles
                LIMIT %s
                """
                
                cursor.execute(query, (limit,))
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                result = []
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    row_dict['personality'] = row_dict['personality'] if row_dict['personality'] else {}
                    row_dict['ideal_for'] = row_dict['ideal_for'] if row_dict['ideal_for'] else {}
                    row_dict['best_languages'] = row_dict['best_languages'] if row_dict['best_languages'] else []
                    result.append(row_dict)
                
                return result

    def search_speaker_profiles(self,
                              gender: Optional[str] = None,
                              accent: Optional[str] = None,
                              topic: Optional[str] = None,
                              language: Optional[str] = None,
                              voice_accent: Optional[str] = None) -> List[Dict]:
        """Search for speaker profiles based on given criteria."""
        from create_audio.openai_utils import GetBestVoiceID
        
        try:
            # First try to get best voice using OpenAI
            best_voice = GetBestVoiceID(
                voice_accent=voice_accent or accent,
                language=language or "english",
                topic=topic or "",
                mood="casual",
                gender=gender,
                all_voices_records=self.get_voice_records(limit=30)
            )
            
            
            # If we got a valid voice, return it as a speaker profile
            if best_voice and best_voice.get('voice_id'):
                # Get full voice details from database
                with self.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            SELECT sp.*, ev.name as voice_name 
                            FROM speaker_profiles sp
                            LEFT JOIN elevenlabs_voices ev ON sp.voice_id = ev.voice_id
                            WHERE sp.voice_id = %s
                        """, (best_voice['voice_id'],))
                        columns = [desc[0] for desc in cursor.description]
                        row = cursor.fetchone()
                        if row:
                            return [self._process_speaker_row(dict(zip(columns, row)))]
        
        except Exception as e:
            logger.warning(f"OpenAI voice selection failed: {str(e)}, falling back to database search")
        
        # Fallback to database search if OpenAI selection fails or no matching voice found
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT sp.*, ev.name as voice_name 
                    FROM speaker_profiles sp
                    LEFT JOIN elevenlabs_voices ev ON sp.voice_id = ev.voice_id
                    WHERE 1=1
                """
                params = []
                
                if gender:
                    query += " AND sp.gender = %s"
                    params.append(gender)
                if accent or voice_accent:
                    query += " AND sp.accent = %s"
                    params.append(voice_accent or accent)
                if language:
                    query += " AND sp.best_languages LIKE %s"
                    params.append(f'%{language}%')
                if topic:
                    query += " AND sp.ideal_for LIKE %s"
                    params.append(f'%{topic}%')
                
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                return [self._process_speaker_row(dict(zip(columns, row))) for row in rows]

    def select_speakers_from_db(self, topic: str, conversation_mood: str, language: str = "english", voice_accent: str = "American") -> List[Dict]:
        """
        Select appropriate speakers from the database based on topic and mood.
        
        Args:
            topic: The conversation topic
            conversation_mood: Mood/style of the conversation
            language: Language for conversation
            voice_accent: Preferred accent for voices
        
        Returns:
            List of speaker dictionaries with voice IDs and metadata
        """
        try:
            db = PodcastDB()
            
            # Get voice records that match our criteria
            voice_records = db.get_voice_records()
            if not voice_records:
                raise ValueError(f"No voice records found")
            
            # For now, just return the first two voices
            # In a real implementation, we would use more sophisticated matching
            selected_voices = voice_records[:2]
            
            # Format speakers with required metadata
            speakers = []
            for i, voice in enumerate(selected_voices):
                speaker = {
                    "name": f"Speaker{i+1}",
                    "voice_id": voice["voice_id"],
                    "language": language,
                    "accent": voice_accent,
                    "personality": "friendly" if i == 0 else "analytical",
                    "speaking_style": conversation_mood
                }
                speakers.append(speaker)
            
            return speakers
        except Exception as e:
            raise Exception(f"Error selecting speakers: {str(e)}")

    def _process_elevenlabs_row(self, row: Dict) -> Dict:
        row['labels'] = json.loads(row['labels'])
        row['settings'] = json.loads(row['settings'])
        return row

    def _process_speaker_row(self, row: Dict) -> Dict:
        row['personality'] = json.loads(row['personality'])
        row['ideal_for'] = json.loads(row['ideal_for'])
        row['best_languages'] = json.loads(row['best_languages'])
        return row
