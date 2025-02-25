-- Create enum for video privacy status
CREATE TYPE youtube_privacy_status AS ENUM ('private', 'unlisted', 'public');

-- Create enum for video approval status
CREATE TYPE youtube_approval_status AS ENUM ('pending', 'approved', 'rejected');

-- Create enum for video publish status
CREATE TYPE youtube_publish_status AS ENUM ('draft', 'scheduled', 'published', 'failed');

-- Create table for customer's YouTube settings
CREATE TABLE customer_youtube_settings (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    default_privacy_status youtube_privacy_status DEFAULT 'private',
    auto_publish BOOLEAN DEFAULT false,
    require_approval BOOLEAN DEFAULT true,
    default_tags TEXT[],
    default_language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(customer_id)
);

-- Create table for customer's YouTube channels
CREATE TABLE customer_youtube_channels (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    channel_id VARCHAR(50) NOT NULL,
    channel_title VARCHAR(255),
    channel_description TEXT,
    channel_thumbnail_url TEXT,
    credentials_path TEXT NOT NULL,
    refresh_token TEXT,
    access_token TEXT,
    token_expiry TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(customer_id, channel_id)
);

-- Create table for channel playlists
CREATE TABLE customer_youtube_playlists (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER REFERENCES customer_youtube_channels(id),
    playlist_id VARCHAR(50) NOT NULL,
    playlist_title VARCHAR(255),
    playlist_description TEXT,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(channel_id, playlist_id)
);

-- Create table for video metadata templates
CREATE TABLE youtube_video_templates (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    template_name VARCHAR(100) NOT NULL,
    title_template TEXT,
    description_template TEXT,
    tags TEXT[],
    privacy_status youtube_privacy_status DEFAULT 'private',
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(customer_id, template_name)
);

-- Create table for video metadata
CREATE TABLE youtube_video_metadata (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES podcast_jobs(id),
    customer_id VARCHAR(50) NOT NULL,
    channel_id INTEGER REFERENCES customer_youtube_channels(id),
    playlist_id INTEGER REFERENCES customer_youtube_playlists(id),
    template_id INTEGER REFERENCES youtube_video_templates(id),
    video_path_id INTEGER REFERENCES video_paths(id),
    title TEXT NOT NULL,
    description TEXT,
    tags TEXT[],
    thumbnail_path TEXT,
    language VARCHAR(10) DEFAULT 'en',
    privacy_status youtube_privacy_status DEFAULT 'private',
    approval_status youtube_approval_status DEFAULT 'pending',
    approval_notes TEXT,
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    publish_status youtube_publish_status DEFAULT 'draft',
    scheduled_publish_time TIMESTAMP,
    youtube_video_id VARCHAR(50),
    publish_error TEXT,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster lookups
CREATE INDEX idx_youtube_metadata_customer ON youtube_video_metadata(customer_id);
CREATE INDEX idx_youtube_metadata_job ON youtube_video_metadata(job_id);
CREATE INDEX idx_youtube_metadata_approval ON youtube_video_metadata(approval_status);
CREATE INDEX idx_youtube_metadata_publish ON youtube_video_metadata(publish_status);
CREATE INDEX idx_youtube_channels_customer ON customer_youtube_channels(customer_id);

-- Add trigger function for updating timestamps
CREATE OR REPLACE FUNCTION update_youtube_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updating timestamps
CREATE TRIGGER update_customer_youtube_settings_timestamp
    BEFORE UPDATE ON customer_youtube_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_youtube_updated_at_column();

CREATE TRIGGER update_customer_youtube_channels_timestamp
    BEFORE UPDATE ON customer_youtube_channels
    FOR EACH ROW
    EXECUTE FUNCTION update_youtube_updated_at_column();

CREATE TRIGGER update_customer_youtube_playlists_timestamp
    BEFORE UPDATE ON customer_youtube_playlists
    FOR EACH ROW
    EXECUTE FUNCTION update_youtube_updated_at_column();

CREATE TRIGGER update_youtube_video_templates_timestamp
    BEFORE UPDATE ON youtube_video_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_youtube_updated_at_column();

CREATE TRIGGER update_youtube_video_metadata_timestamp
    BEFORE UPDATE ON youtube_video_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_youtube_updated_at_column();

-- Add comments
COMMENT ON TABLE customer_youtube_settings IS 'Stores customer-specific YouTube settings and preferences';
COMMENT ON TABLE customer_youtube_channels IS 'Stores customer YouTube channel information and authentication details';
COMMENT ON TABLE customer_youtube_playlists IS 'Stores YouTube playlist information for each channel';
COMMENT ON TABLE youtube_video_templates IS 'Stores templates for video metadata';
COMMENT ON TABLE youtube_video_metadata IS 'Stores video metadata and publishing status';

-- Drop previously created tables as they are replaced by new schema
DROP TABLE IF EXISTS youtube_videos CASCADE;
DROP TABLE IF EXISTS youtube_playlists CASCADE;
DROP TABLE IF EXISTS youtube_channels CASCADE;
