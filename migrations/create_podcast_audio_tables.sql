-- Drop tables if they exist
DROP TABLE IF EXISTS podcast_audio_details;

-- Create podcast_audio_details table
CREATE TABLE podcast_audio_details (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) NOT NULL,
    customer_id VARCHAR(255) NOT NULL,
    
    -- Voice-over text content
    welcome_voiceover_text TEXT,
    conversation_data JSONB,  -- Store the full conversation JSON
    intro_voiceover_text TEXT,
    podcast_intro_voiceover TEXT,
    default_podcast_intro_text TEXT,  -- Added default podcast intro text
    
    -- Audio file paths
    welcome_audio_path VARCHAR(1024),
    conversation_audio_path VARCHAR(1024),
    intro_audio_path VARCHAR(1024),
    podcast_intro_audio_path VARCHAR(1024),
    default_podcast_intro_audio_path VARCHAR(1024),  -- Added default podcast intro audio path
    final_mix_path VARCHAR(1024),
    
    -- Schema and metadata
    schema_path VARCHAR(1024),
    transistor_episode_id VARCHAR(255),
    transistor_show_id VARCHAR(255),
    transistor_audio_url TEXT,
    
    -- Status and metadata
    status VARCHAR(50) DEFAULT 'pending',  -- pending, processing, completed, failed
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Additional metadata
    voice_settings JSONB,  -- Store voice configuration
    request_data JSONB,    -- Store original request data
    
    -- Indexes
    CONSTRAINT unique_job_id UNIQUE (job_id)
);

-- Create index for faster lookups
CREATE INDEX idx_podcast_audio_job_id ON podcast_audio_details(job_id);
CREATE INDEX idx_podcast_audio_customer_id ON podcast_audio_details(customer_id);
CREATE INDEX idx_podcast_audio_status ON podcast_audio_details(status);
CREATE INDEX idx_podcast_audio_created_at ON podcast_audio_details(created_at);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_podcast_audio_updated_at
    BEFORE UPDATE ON podcast_audio_details
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE podcast_audio_details IS 'Stores podcast audio generation details including voice-over text and file paths';
COMMENT ON COLUMN podcast_audio_details.job_id IS 'Unique identifier for the audio generation job';
COMMENT ON COLUMN podcast_audio_details.customer_id IS 'ID of the customer who requested the audio generation';
COMMENT ON COLUMN podcast_audio_details.welcome_voiceover_text IS 'Welcome message voice-over text';
COMMENT ON COLUMN podcast_audio_details.conversation_data IS 'Full conversation data in JSON format';
COMMENT ON COLUMN podcast_audio_details.intro_voiceover_text IS 'Introduction voice-over text';
COMMENT ON COLUMN podcast_audio_details.podcast_intro_voiceover IS 'Podcast introduction voice-over text';
COMMENT ON COLUMN podcast_audio_details.default_podcast_intro_text IS 'Default podcast introduction text';
COMMENT ON COLUMN podcast_audio_details.welcome_audio_path IS 'Path to the welcome audio file';
COMMENT ON COLUMN podcast_audio_details.conversation_audio_path IS 'Path to the main conversation audio file';
COMMENT ON COLUMN podcast_audio_details.intro_audio_path IS 'Path to the introduction audio file';
COMMENT ON COLUMN podcast_audio_details.podcast_intro_audio_path IS 'Path to the podcast introduction audio file';
COMMENT ON COLUMN podcast_audio_details.default_podcast_intro_audio_path IS 'Path to the default podcast introduction audio file';
COMMENT ON COLUMN podcast_audio_details.final_mix_path IS 'Path to the final mixed audio file';
COMMENT ON COLUMN podcast_audio_details.schema_path IS 'Path to the conversation schema file';
COMMENT ON COLUMN podcast_audio_details.transistor_episode_id IS 'Episode ID from Transistor.fm';
COMMENT ON COLUMN podcast_audio_details.transistor_show_id IS 'Show ID from Transistor.fm';
COMMENT ON COLUMN podcast_audio_details.transistor_audio_url IS 'Audio URL from Transistor.fm';
COMMENT ON COLUMN podcast_audio_details.status IS 'Current status of the audio generation process';
COMMENT ON COLUMN podcast_audio_details.voice_settings IS 'Voice configuration settings in JSON format';
COMMENT ON COLUMN podcast_audio_details.request_data IS 'Original request data in JSON format';
