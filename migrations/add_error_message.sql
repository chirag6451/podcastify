-- Add error_message column
ALTER TABLE youtube_video_metadata
ADD COLUMN error_message TEXT;
