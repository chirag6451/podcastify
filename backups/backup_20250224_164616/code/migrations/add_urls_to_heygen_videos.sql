-- Add URL and path columns to heygen_videos table
ALTER TABLE heygen_videos
ADD COLUMN video_url TEXT,
ADD COLUMN thumbnail_url TEXT,
ADD COLUMN video_path TEXT,
ADD COLUMN thumbnail_path TEXT;
