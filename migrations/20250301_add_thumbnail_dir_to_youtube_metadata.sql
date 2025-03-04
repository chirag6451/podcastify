-- Migration: Add thumbnail_dir to youtube_video_metadata
-- Created at: 2025-03-01 18:09:36
-- Description: Adds a column to store the directory path for YouTube video thumbnails

ALTER TABLE youtube_video_metadata
ADD COLUMN IF NOT EXISTS thumbnail_dir VARCHAR(255);

-- Add comment to the column
COMMENT ON COLUMN youtube_video_metadata.thumbnail_dir IS 'Directory path where YouTube video thumbnails are stored';
