-- Add approval columns to youtube_video_metadata
ALTER TYPE youtube_publish_status ADD VALUE IF NOT EXISTS 'pending' BEFORE 'published';
ALTER TYPE youtube_publish_status ADD VALUE IF NOT EXISTS 'approved' BEFORE 'published';

-- Add approval tracking columns
ALTER TABLE youtube_video_metadata 
ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS approved_by VARCHAR(255),
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;

-- Create video_files table if not exists
CREATE TABLE IF NOT EXISTS video_files (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add video_path_id to youtube_video_metadata if not exists
ALTER TABLE youtube_video_metadata 
ADD COLUMN IF NOT EXISTS video_path_id INTEGER REFERENCES video_files(id);
