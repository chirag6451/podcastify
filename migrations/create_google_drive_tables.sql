-- Drop existing tables if they exist
DROP TABLE IF EXISTS google_drive_files;
DROP TABLE IF EXISTS customer_drive_folders;

-- Create table for storing Google Drive folder information
CREATE TABLE IF NOT EXISTS customer_drive_folders (
    folder_id VARCHAR(255) PRIMARY KEY,
    customer_id VARCHAR(255) NOT NULL,
    folder_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(customer_id, folder_id)
);

-- Create index on folder_id for foreign key reference
CREATE INDEX IF NOT EXISTS idx_customer_drive_folders_folder_id ON customer_drive_folders(folder_id);

-- Create table for storing Google Drive file information
CREATE TABLE IF NOT EXISTS google_drive_files (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(255) NOT NULL,
    file_id VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    folder_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(customer_id, file_id),
    FOREIGN KEY (folder_id) REFERENCES customer_drive_folders(folder_id) ON DELETE SET NULL
);
