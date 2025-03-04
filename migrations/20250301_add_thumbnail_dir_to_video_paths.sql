-- Migration: Add thumbnail_dir to video_paths
-- Created at: 2025-03-01 18:12:22
-- Description: Adds a column to store the directory path for video thumbnails

ALTER TABLE video_paths
ADD COLUMN IF NOT EXISTS thumbnail_dir VARCHAR(255);

-- Add comment to the column
COMMENT ON COLUMN video_paths.thumbnail_dir IS 'Directory path where video thumbnails are stored';
