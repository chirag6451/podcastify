-- Add tracking columns to video_paths table
ALTER TABLE video_paths
ADD COLUMN retry_count INTEGER DEFAULT 0,
ADD COLUMN error_details TEXT,
ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP,
ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;

-- Add comments for documentation
COMMENT ON COLUMN video_paths.retry_count IS 'Number of times video creation has been retried';
COMMENT ON COLUMN video_paths.error_details IS 'Details of any errors encountered during video creation';
COMMENT ON COLUMN video_paths.created_at IS 'Timestamp when the record was created';
COMMENT ON COLUMN video_paths.updated_at IS 'Timestamp when the record was last updated';

-- Create or replace the update trigger to handle retry_count and error_details
CREATE OR REPLACE FUNCTION update_video_paths_tracking_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    -- Always update updated_at on any column change
    NEW.updated_at = CURRENT_TIMESTAMP;
    
    -- If status is changing to 'failed', increment retry count
    IF OLD.status != 'failed' AND NEW.status = 'failed' THEN
        NEW.retry_count = COALESCE(OLD.retry_count, 0) + 1;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop existing trigger if it exists
DROP TRIGGER IF EXISTS video_paths_tracking_updated ON video_paths;

-- Create new trigger for tracking updates
CREATE TRIGGER video_paths_tracking_updated
    BEFORE UPDATE
    ON video_paths
    FOR EACH ROW
    EXECUTE FUNCTION update_video_paths_tracking_updated_at();
