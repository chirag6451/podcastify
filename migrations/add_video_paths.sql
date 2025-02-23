-- Add customer_id to podcast_jobs table
ALTER TABLE podcast_jobs
ADD COLUMN customer_id INTEGER;

-- Create video_paths table
CREATE TABLE video_paths (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL,
    audio_path VARCHAR,
    welcome_audio_path VARCHAR,
    intro_video_path VARCHAR,
    bumper_video_path VARCHAR,
    short_video_path VARCHAR,
    main_video_path VARCHAR,
    outro_video_path VARCHAR,
    welcome_video_avatar_path VARCHAR,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES podcast_jobs(id) ON DELETE CASCADE
);

-- Create index on job_id for faster lookups
CREATE INDEX ix_video_paths_job_id ON video_paths(job_id);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_video_paths_updated_at
    BEFORE UPDATE ON video_paths
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
