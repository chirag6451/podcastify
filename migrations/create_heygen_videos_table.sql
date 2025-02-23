-- Create heygen_videos table
CREATE TABLE heygen_videos (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    heygen_video_id VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'pending',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES podcast_jobs(id) ON DELETE CASCADE
);

-- Create index on task_id for faster lookups
CREATE INDEX ix_heygen_videos_task_id ON heygen_videos(task_id);

-- Create index on heygen_video_id for status checks
CREATE INDEX ix_heygen_videos_video_id ON heygen_videos(heygen_video_id);
