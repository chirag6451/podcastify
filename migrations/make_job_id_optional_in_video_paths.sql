-- Make job_id optional in video_paths table
ALTER TABLE video_paths ALTER COLUMN job_id DROP NOT NULL;
