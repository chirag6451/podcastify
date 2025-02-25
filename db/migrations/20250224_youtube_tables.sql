-- Create table for storing YouTube channels
CREATE TABLE IF NOT EXISTS user_youtube_channels (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    channel_id VARCHAR(255) NOT NULL,
    channel_name VARCHAR(255) NOT NULL,
    channel_url VARCHAR(512) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, channel_id)
);

-- Create table for storing YouTube playlists
CREATE TABLE IF NOT EXISTS user_youtube_playlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    channel_id VARCHAR(255) NOT NULL,
    playlist_id VARCHAR(255) NOT NULL,
    playlist_name VARCHAR(255) NOT NULL,
    playlist_url VARCHAR(512) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, playlist_id)
);

-- Create table for tracking YouTube uploads
CREATE TABLE IF NOT EXISTS user_youtube_uploads (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    channel_id VARCHAR(255) NOT NULL,
    playlist_id VARCHAR(255),
    video_id VARCHAR(255),
    video_title VARCHAR(255) NOT NULL,
    video_description TEXT,
    video_url VARCHAR(512),
    original_file_name VARCHAR(255) NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    upload_status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, video_id)
);
