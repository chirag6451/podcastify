-- Add YouTube channel and playlist columns to podcast_jobs table
ALTER TABLE podcast_jobs 
ADD COLUMN youtube_channel_id VARCHAR(255),
ADD COLUMN youtube_playlist_id VARCHAR(255);
