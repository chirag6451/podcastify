CREATE TABLE IF NOT EXISTS google_auth (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    google_id TEXT NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_expiry TIMESTAMP WITH TIME ZONE,
    profile_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
