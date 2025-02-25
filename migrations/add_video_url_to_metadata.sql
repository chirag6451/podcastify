-- Add video_url column to youtube_video_metadata
ALTER TABLE youtube_video_metadata
ADD COLUMN video_url TEXT;
