-- Add customer_id column to video_paths table
ALTER TABLE video_paths
ADD COLUMN customer_id VARCHAR;

-- Add index for faster lookups
CREATE INDEX idx_video_paths_customer_id ON video_paths(customer_id);

-- Update existing records to copy customer_id from podcast_jobs
UPDATE video_paths vp
SET customer_id = pj.customer_id
FROM podcast_jobs pj
WHERE vp.job_id = pj.id;
