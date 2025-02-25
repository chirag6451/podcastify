-- Add new columns to google_auth table
ALTER TABLE google_auth
ADD COLUMN IF NOT EXISTS token_uri VARCHAR(255),
ADD COLUMN IF NOT EXISTS client_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS client_secret VARCHAR(255);
