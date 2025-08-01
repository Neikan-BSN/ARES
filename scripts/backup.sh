#!/bin/bash
# Simple backup script for project data

set -e

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="project_backup_${TIMESTAMP}.tar.gz"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[BACKUP]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

log "Creating project backup..."

# Create backup archive
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}" \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='.venv' \
    --exclude='node_modules' \
    --exclude='*.log' \
    --exclude='backups' \
    --exclude='temp' \
    --exclude='.pytest_cache' \
    --exclude='.mypy_cache' \
    --exclude='.ruff_cache' \
    .

success "Backup created: ${BACKUP_DIR}/${BACKUP_NAME}"

# Clean up old backups (keep last 10)
log "Cleaning up old backups..."
cd "$BACKUP_DIR"
ls -t project_backup_*.tar.gz | tail -n +11 | xargs rm -f || true
cd - > /dev/null

success "Backup process completed"
