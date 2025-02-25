-- Create table for storing Google authentication data
CREATE TABLE IF NOT EXISTS google_auth (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    google_id VARCHAR(255) NOT NULL UNIQUE,
    access_token TEXT,
    refresh_token TEXT,
    token_expiry TIMESTAMP,
    profile_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(email)
);

-- Add indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_google_auth_user_id ON google_auth(user_id);
CREATE INDEX IF NOT EXISTS idx_google_auth_email ON google_auth(email);
CREATE INDEX IF NOT EXISTS idx_google_auth_google_id ON google_auth(google_id);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS
$$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update the updated_at column
DROP TRIGGER IF EXISTS update_google_auth_updated_at ON google_auth;
CREATE TRIGGER update_google_auth_updated_at
    BEFORE UPDATE ON google_auth
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
