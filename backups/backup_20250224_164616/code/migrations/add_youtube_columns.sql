-- Create table for YouTube channel configurations
CREATE TABLE youtube_channels (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    channel_id VARCHAR(50) NOT NULL,
    channel_title VARCHAR(255),
    credentials_path TEXT,
    token_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(customer_id, channel_id)
);

-- Create table for YouTube playlists
CREATE TABLE youtube_playlists (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER REFERENCES youtube_channels(id),
    playlist_id VARCHAR(50) NOT NULL,
    playlist_title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(channel_id, playlist_id)
);

-- Create table for YouTube video uploads
CREATE TABLE youtube_videos (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES podcast_jobs(id),
    customer_id VARCHAR(50) NOT NULL,
    channel_id INTEGER REFERENCES youtube_channels(id),
    playlist_id INTEGER REFERENCES youtube_playlists(id),
    video_path_id INTEGER REFERENCES video_paths(id),
    youtube_video_id VARCHAR(50),
    title TEXT,
    description TEXT,
    tags TEXT[],
    privacy_status VARCHAR(20) DEFAULT 'private',
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    upload_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for faster lookups
CREATE INDEX idx_youtube_videos_status ON youtube_videos(status);
CREATE INDEX idx_youtube_videos_customer ON youtube_videos(customer_id);
CREATE INDEX idx_youtube_videos_job ON youtube_videos(job_id);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_youtube_channels_updated_at
    BEFORE UPDATE ON youtube_channels
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_youtube_playlists_updated_at
    BEFORE UPDATE ON youtube_playlists
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_youtube_videos_updated_at
    BEFORE UPDATE ON youtube_videos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments
COMMENT ON TABLE youtube_channels IS 'Stores YouTube channel configurations for customers';
COMMENT ON TABLE youtube_playlists IS 'Stores YouTube playlist information';
COMMENT ON TABLE youtube_videos IS 'Stores YouTube video upload details and status';

-- Remove previously added columns from video_paths as they are now in youtube_videos
ALTER TABLE video_paths
DROP COLUMN IF EXISTS youtube_id,
DROP COLUMN IF EXISTS youtube_status,
DROP COLUMN IF EXISTS youtube_error,
DROP COLUMN IF EXISTS youtube_upload_date,
DROP COLUMN IF EXISTS youtube_title,
DROP COLUMN IF EXISTS youtube_description,
DROP COLUMN IF EXISTS youtube_tags;
