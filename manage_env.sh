#!/bin/bash

# Function to create directories if they don't exist
create_dirs() {
    mkdir -p staticfiles_dev
    mkdir -p media_dev
    mkdir -p staticfiles_prod
    mkdir -p media_prod
}

# Function to collect static files for development
collect_static_dev() {
    echo "Collecting static files for development..."
    python3 manage.py collectstatic --settings=re_arqui.settings --no-input
}

# Function to collect static files for production
collect_static_prod() {
    echo "Collecting static files for production..."
    python3 manage.py collectstatic --settings=re_arqui.settings_prod --no-input
}

# Function to sync media files from dev to prod
sync_media_to_prod() {
    echo "Syncing media files from development to production..."
    echo "This will copy all media files from development to production."
    echo "Any files in production that don't exist in development will be deleted."
    read -p "Are you sure you want to continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        rsync -av --delete media_dev/ media_prod/
        echo "Media files synced to production successfully!"
    else
        echo "Sync cancelled."
    fi
}

# Create necessary directories
create_dirs

# Parse command line arguments
case "$1" in
    "dev")
        collect_static_dev
        echo "Development environment is ready!"
        ;;
    "prod")
        collect_static_prod
        echo "Production environment is ready!"
        ;;
    "sync-to-prod")
        sync_media_to_prod
        ;;
    *)
        echo "Usage: $0 {dev|prod|sync-to-prod}"
        echo "  dev           - Set up development environment"
        echo "  prod          - Set up production environment"
        echo "  sync-to-prod  - Sync media files from dev to prod"
        exit 1
        ;;
esac 