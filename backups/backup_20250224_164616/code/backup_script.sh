#!/bin/bash

# Exit on error
set -e

# Configuration
PROJECT_ROOT=$(pwd)
PROJECT_NAME=$(basename "$PROJECT_ROOT")
BACKUP_DIR="./backups"

# Create timestamp for backup folder
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CURRENT_BACKUP_DIR="$BACKUP_DIR/backup_$TIMESTAMP"

# Function to perform backup
perform_backup() {
    local CURRENT_BACKUP_DIR="$1"
    
    # Get backup details from user first
    echo "Please provide backup details:"
    read -p "Enter backup description: " description
    read -p "Enter version/tag (optional): " version
    
    # Create backup directory
    mkdir -p "$CURRENT_BACKUP_DIR"/{code,sensitive}
    
    # Backup code files
    echo "Backing up code files..."
    rsync -av --progress \
        --exclude="node_modules" \
        --exclude="venv" \
        --exclude="__pycache__" \
        --exclude=".git" \
        --exclude="backups" \
        --exclude="sensitive" \
        . "$CURRENT_BACKUP_DIR/code/"
    
    # Backup database
    echo "Backing up database..."
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
        PGPASSWORD=$POSTGRES_PASSWORD pg_dump \
            -h $POSTGRES_HOST \
            -p $POSTGRES_PORT \
            -U $POSTGRES_USER \
            -d $POSTGRES_DB \
            -F c \
            -f "$CURRENT_BACKUP_DIR/database_backup.dump"
        
        if [ $? -ne 0 ]; then
            echo "Error: Database backup failed!"
            exit 1
        else
            echo "Database backup completed successfully"
        fi
    else
        echo "Error: .env file not found"
        exit 1
    fi
    
    # Create manifest file
    cat > "$CURRENT_BACKUP_DIR/manifest.txt" << EOF
Backup Details:
--------------
Date: $(date)
Description: $description
Version/Tag: ${version:-"N/A"}
Files:
$(ls -R "$CURRENT_BACKUP_DIR")
EOF
    
    # Create symlink to latest backup (only if this is not the first backup)
    if [[ "$CURRENT_BACKUP_DIR" != *"first_backup"* ]]; then
        rm -f "$BACKUP_DIR/latest"  # Remove old symlink if exists
        ln -s "$CURRENT_BACKUP_DIR" "$BACKUP_DIR/latest"
    fi
    
    echo "Backup completed successfully!"
    echo "Backup location: $CURRENT_BACKUP_DIR"
    echo "Files backed up:"
    ls -lh "$CURRENT_BACKUP_DIR"
    echo "A manifest file has been created at: $CURRENT_BACKUP_DIR/manifest.txt"
}

# Main script
case "$1" in
    "backup")
        perform_backup "$CURRENT_BACKUP_DIR"
        ;;
    *)
        echo "Usage: $0 backup"
        exit 1
        ;;
esac
