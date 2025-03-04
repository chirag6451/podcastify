-- Add approval related columns to podcast_audio_details table
ALTER TABLE podcast_audio_details
    -- Approval status
    ADD COLUMN approval_status VARCHAR(50) DEFAULT 'draft' CHECK (approval_status IN ('draft', 'pending_approval', 'approved', 'rejected')),
    ADD COLUMN approved_by VARCHAR(255),
    ADD COLUMN approved_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN rejected_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN rejection_reason TEXT,
    
    -- Additional metadata
    ADD COLUMN approved_version INTEGER DEFAULT 1,
    ADD COLUMN approval_comments TEXT,
    ADD COLUMN last_modified_by VARCHAR(255),
    
    -- Timestamps for tracking
    ADD COLUMN submitted_for_approval_at TIMESTAMP WITH TIME ZONE;

-- Add indexes for commonly queried columns
CREATE INDEX idx_podcast_audio_approval_status ON podcast_audio_details(approval_status);
CREATE INDEX idx_podcast_audio_approved_at ON podcast_audio_details(approved_at);

-- Add comments
COMMENT ON COLUMN podcast_audio_details.approval_status IS 'Current approval status (draft, pending_approval, approved, rejected)';
COMMENT ON COLUMN podcast_audio_details.approved_by IS 'Username of the person who approved the audio';
COMMENT ON COLUMN podcast_audio_details.approved_at IS 'Timestamp when the audio was approved';
COMMENT ON COLUMN podcast_audio_details.rejected_at IS 'Timestamp when the audio was rejected';
COMMENT ON COLUMN podcast_audio_details.rejection_reason IS 'Reason for rejection if status is rejected';
COMMENT ON COLUMN podcast_audio_details.approved_version IS 'Version number of the approved audio';
COMMENT ON COLUMN podcast_audio_details.approval_comments IS 'Any additional comments during approval process';
COMMENT ON COLUMN podcast_audio_details.last_modified_by IS 'Username of the person who last modified the record';
COMMENT ON COLUMN podcast_audio_details.submitted_for_approval_at IS 'Timestamp when the audio was submitted for approval';
