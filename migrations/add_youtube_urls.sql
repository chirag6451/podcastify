-- Add columns for video URL and thumbnail URLs
ALTER TABLE youtube_video_metadata
ADD COLUMN video_url TEXT,
ADD COLUMN thumbnail_url_default TEXT,
ADD COLUMN thumbnail_url_medium TEXT,
ADD COLUMN thumbnail_url_high TEXT;
