#!/bin/bash

# Make migrations
python manage.py migrate --settings=re_arqui.settings_prod --no-input

# Collect static files
python manage.py collectstatic --settings=re_arqui.settings_prod --no-input

# Start Gunicorn using Python module approach
python -m gunicorn --bind=0.0.0.0:8000 --workers=2 re_arqui.wsgi:application 