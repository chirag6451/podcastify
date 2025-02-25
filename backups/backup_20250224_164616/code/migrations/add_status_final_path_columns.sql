-- Add status and final_video_path columns to video_paths table
ALTER TABLE video_paths
ADD COLUMN status VARCHAR(50) DEFAULT 'pending',
ADD COLUMN final_video_path VARCHAR;

-- Add comments for documentation
COMMENT ON COLUMN video_paths.status IS 'Current status of the video (e.g., pending, processing, completed, failed)';
COMMENT ON COLUMN video_paths.final_video_path IS 'Path to the final concatenated video file';

-- Create index on status for faster queries
CREATE INDEX ix_video_paths_status ON video_paths(status);

-- Update function to maintain updated_at when status changes
CREATE OR REPLACE FUNCTION update_video_paths_status_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status OR 
       OLD.final_video_path IS DISTINCT FROM NEW.final_video_path THEN
        NEW.updated_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for status updates
CREATE TRIGGER video_paths_status_updated
    BEFORE UPDATE OF status, final_video_path
    ON video_paths
    FOR EACH ROW
    EXECUTE FUNCTION update_video_paths_status_updated_at();
