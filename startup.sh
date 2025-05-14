#!/bin/bash

# Make migrations
python manage.py migrate --settings=re_arqui.settings_prod --no-input

# Collect static files
python manage.py collectstatic --settings=re_arqui.settings_prod --no-input

# Copy media files to the staticfiles/media directory for WhiteNoise to serve
mkdir -p staticfiles/media
cp -r media/* staticfiles/media/ 2>/dev/null || true

# Start Gunicorn using Python module approach
python -m gunicorn --bind=0.0.0.0:8000 --workers=2 re_arqui.wsgi:application 