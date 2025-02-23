-- Add is_heygen_video column to video_paths table
ALTER TABLE video_paths
ADD COLUMN is_heygen_video BOOLEAN DEFAULT FALSE;

-- Update existing records where hygen_short_video is not null
UPDATE video_paths
SET is_heygen_video = TRUE
WHERE hygen_short_video IS NOT NULL;
