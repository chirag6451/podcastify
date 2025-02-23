#!/bin/bash

# Exit on error
set -e

# Configuration
PROJECT_ROOT=$(pwd)
PROJECT_NAME=$(basename "$PROJECT_ROOT")
BACKUP_ROOT="${BACKUP_ROOT:-/Users/$(whoami)/backups}"
BACKUP_DIR="$BACKUP_ROOT/$PROJECT_NAME"

# Create timestamp for backup folder
TIMESTAMP=$(date +"%Y-%m-%d_%H%M")

# Check if this is the first backup
if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A $BACKUP_DIR 2>/dev/null)" ]; then
    CURRENT_BACKUP_DIR="$BACKUP_DIR/first_backup"
else
    CURRENT_BACKUP_DIR="$BACKUP_DIR/backup_$TIMESTAMP"
fi

SENSITIVE_DIR="$CURRENT_BACKUP_DIR/sensitive"

# Tech-specific ignore patterns
COMMON_IGNORES=(
    ".git"
    ".DS_Store"
    "*.log"
    "*.tmp"
    "*.swp"
    ".idea"
    ".vscode"
    "backups"
)

PYTHON_IGNORES=(
    "venv"
    "env"
    "__pycache__"
    "*.pyc"
    ".pytest_cache"
    ".coverage"
    "dist"
    "build"
    "*.egg-info"
)

NODE_IGNORES=(
    "node_modules"
    "npm-debug.log"
    "yarn-debug.log"
    "yarn-error.log"
    ".next"
    ".nuxt"
    "dist"
    "build"
    ".cache"
)

REACT_IGNORES=(
    "build"
    "coverage"
    ".env.local"
    ".env.development.local"
    ".env.test.local"
    ".env.production.local"
)

# Sensitive files patterns
SENSITIVE_PATTERNS=(
    ".env"
    "*.env*"
    "*config*.json"
    "*secret*.json"
    "*credential*.json"
    "*token*.json"
    "*key*.json"
    "*password*.txt"
)

# Function to detect project type
detect_project_type() {
    local types=()
    
    # Python detection
    if [ -f "requirements.txt" ] || [ -f "setup.py" ] || [ -f "Pipfile" ] || [ -d "venv" ]; then
        types+=("python")
    fi
    
    # Node.js detection
    if [ -f "package.json" ]; then
        types+=("node")
        
        # React detection
        if grep -q "react" "package.json"; then
            types+=("react")
        fi
        
        # Next.js detection
        if grep -q "next" "package.json"; then
            types+=("next")
        fi
    fi
    
    echo "${types[@]}"
}

# Function to build ignore patterns based on project type
build_ignore_patterns() {
    local project_types=($1)
    local ignore_patterns=("${COMMON_IGNORES[@]}")
    
    for type in "${project_types[@]}"; do
        case $type in
            "python")
                ignore_patterns+=("${PYTHON_IGNORES[@]}")
                ;;
            "node")
                ignore_patterns+=("${NODE_IGNORES[@]}")
                ;;
            "react"|"next")
                ignore_patterns+=("${REACT_IGNORES[@]}")
                ;;
        esac
    done
    
    # Convert to rsync format
    local rsync_patterns=()
    for pattern in "${ignore_patterns[@]}"; do
        rsync_patterns+=("--exclude=$pattern")
    done
    
    echo "${rsync_patterns[@]}"
}

# Function to create backup manifest
create_manifest() {
    local manifest_file="$CURRENT_BACKUP_DIR/manifest.txt"
    
    # Get user comment
    echo "Please enter a comment describing the current state/changes (press Enter when done):"
    read -r USER_COMMENT
    
    # Create manifest file with header and user comment
    cat > "$manifest_file" << EOF
=== Backup Manifest ===
Timestamp: $TIMESTAMP
Project: $PROJECT_NAME
Comment: $USER_COMMENT

=== Project Information ===
Project Types: $(detect_project_type)
Total Files: $(find . -type f | wc -l)
Git Status: $(if [ -d ".git" ]; then git status --porcelain; else echo "Not a git repository"; fi)

=== Environment Information ===
OS: $(uname -s)
Python Version: $(if command -v python3 >/dev/null 2>&1; then python3 --version; else echo "Not installed"; fi)
Node Version: $(if command -v node >/dev/null 2>&1; then node --version; else echo "Not installed"; fi)
Git Branch: $(if [ -d ".git" ]; then git branch --show-current; else echo "Not a git repository"; fi)

=== Files Included ===
$(find . -type f -not -path '*/\.*' | sort)

=== Sensitive Files (Stored Separately) ===
$(find "$SENSITIVE_DIR" -type f 2>/dev/null | sed 's|.*/||' || echo "None")
EOF
    
    echo "Manifest created at: $manifest_file"
}

# Function to backup sensitive files
backup_sensitive_files() {
    echo "Backing up sensitive files..."
    mkdir -p "$SENSITIVE_DIR"
    
    # Copy .env file first (if it exists)
    if [ -f ".env" ]; then
        cp ".env" "$SENSITIVE_DIR/"
        echo "Backed up .env file"
    fi
    
    # Then handle other sensitive files
    for pattern in "${SENSITIVE_PATTERNS[@]}"; do
        find . -type f -name "$pattern" ! -path "*/venv/*" ! -path "*/.git/*" -exec cp --parents {} "$SENSITIVE_DIR/" \;
    done
    
    echo "Sensitive files backup completed"
}

# Function to create backup
create_backup() {
    local project_types=$(detect_project_type)
    echo "Detected project types: $project_types"
    
    # Create backup directories
    mkdir -p "$CURRENT_BACKUP_DIR"
    
    # Create manifest
    create_manifest
    
    # Build ignore patterns
    local ignore_patterns=$(build_ignore_patterns "$project_types")
    
    # Create project archive
    echo "Creating project backup..."
    rsync -av --progress \
        $ignore_patterns \
        --exclude="$BACKUP_ROOT" \
        . "$CURRENT_BACKUP_DIR/project_files/"
    
    # Backup sensitive files
    backup_sensitive_files
    
    # Create symlink to latest backup (only if this is not the first backup)
    if [[ "$CURRENT_BACKUP_DIR" != *"first_backup"* ]]; then
        rm -f "$BACKUP_DIR/latest"  # Remove old symlink if exists
        ln -sf "$CURRENT_BACKUP_DIR" "$BACKUP_DIR/latest"
    fi
    
    echo "Backup completed successfully!"
    echo "Backup location: $CURRENT_BACKUP_DIR"
    echo "A manifest file has been created at: $CURRENT_BACKUP_DIR/manifest.txt"
}

# Function to list backups
list_backups() {
    echo "Available backups for project $PROJECT_NAME:"
    if [ -d "$BACKUP_DIR" ]; then
        for backup in "$BACKUP_DIR"/backup_*; do
            if [ -d "$backup" ]; then
                size=$(du -sh "$backup" | cut -f1)
                name=$(basename "$backup")
                echo "- $name ($size)"
            fi
        done
    else
        echo "No backups found."
    fi
    
    if [ -L "$BACKUP_DIR/latest" ]; then
        echo ""
        echo "Latest backup: $(readlink "$BACKUP_DIR/latest")"
    fi
}

# Function to restore backup
restore_backup() {
    local source_dir=$1
    
    if [ ! -d "$source_dir" ]; then
        echo "Error: Backup directory not found: $source_dir"
        exit 1
    fi
    
    echo "Restoring from backup: $source_dir"
    
    # Create a backup before restoring
    create_backup
    
    # Restore project files
    echo "Restoring project files..."
    rsync -av --progress "$source_dir/project_files/" .
    
    # Restore sensitive files
    if [ -d "$source_dir/sensitive" ]; then
        echo "Restoring sensitive files..."
        rsync -av --progress "$source_dir/sensitive/" .
    fi
    
    echo "Restore completed successfully!"
}

# Main script
case "$1" in
    "backup")
        create_backup
        ;;
    "list")
        list_backups
        ;;
    "restore")
        if [ -z "$2" ]; then
            echo "Error: Please specify backup directory to restore"
            echo "Usage: $0 restore <backup_directory>"
            exit 1
        fi
        restore_backup "$2"
        ;;
    *)
        echo "Usage: $0 {backup|list|restore <backup_directory>}"
        echo ""
        echo "Environment variables:"
        echo "  BACKUP_ROOT: Root directory for backups (default: ~/backups)"
        exit 1
        ;;
esac
