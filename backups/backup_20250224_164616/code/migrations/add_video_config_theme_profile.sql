-- Add video_config, theme, and profile columns to video_paths table
ALTER TABLE video_paths
ADD COLUMN video_config JSONB DEFAULT '{}',
ADD COLUMN theme VARCHAR DEFAULT 'default',
ADD COLUMN profile VARCHAR DEFAULT 'default';

-- Add comments for documentation
COMMENT ON COLUMN video_paths.video_config IS 'JSON configuration for video creation including resolution, codecs, bitrates etc';
COMMENT ON COLUMN video_paths.theme IS 'Visual theme for the video (e.g., dark, light, modern)';
COMMENT ON COLUMN video_paths.profile IS 'Profile settings for video creation (e.g., high_quality, fast_render)';

-- Update function to maintain updated_at
CREATE OR REPLACE FUNCTION update_video_paths_config_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for config updates
CREATE TRIGGER video_paths_config_updated
    BEFORE UPDATE OF video_config, theme, profile
    ON video_paths
    FOR EACH ROW
    EXECUTE FUNCTION update_video_paths_config_updated_at();
