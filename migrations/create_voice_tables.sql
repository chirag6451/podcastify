-- Create ElevenLabs voices table
CREATE TABLE IF NOT EXISTS elevenlabs_voices (
    voice_id TEXT PRIMARY KEY,
    name TEXT,
    category TEXT,
    description TEXT,
    labels JSONB,  -- Using JSONB for better JSON handling in PostgreSQL
    gender TEXT,
    accent TEXT,
    age TEXT,
    language TEXT,
    use_case TEXT,
    preview_url TEXT,
    settings JSONB  -- Using JSONB for better JSON handling in PostgreSQL
);

-- Create speaker profiles table
CREATE TABLE IF NOT EXISTS speaker_profiles (
    speaker_id TEXT PRIMARY KEY,
    name TEXT,
    voice_id TEXT,  -- Reference to ElevenLabs voice_id
    gender TEXT,
    personality JSONB,  -- Using JSONB for better JSON handling in PostgreSQL
    ideal_for JSONB,   -- Using JSONB for better JSON handling in PostgreSQL
    accent TEXT,
    best_languages JSONB,  -- Using JSONB for better JSON handling in PostgreSQL
    FOREIGN KEY(voice_id) REFERENCES elevenlabs_voices(voice_id)
);
