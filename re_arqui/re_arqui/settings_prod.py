"""
Production Django settings for re_arqui project.
"""

from pathlib import Path
import os
import json

# Import base settings
from .settings import *

# SECURITY WARNING: keep the secret key used in production secret!
# Read secret key from a file
try:
    with open(os.path.join(BASE_DIR, 'secret_key.json')) as f:
        SECRET_KEY = json.load(f)['SECRET_KEY']
except FileNotFoundError:
    # Fallback to the development secret key if file not found
    # This is not ideal for real production but helps with testing
    print("WARNING: Using development secret key in production!")

# SECURITY WARNING: don't run with debug turned on in production!
# Enable debug temporarily to diagnose issues
DEBUG = True

ALLOWED_HOSTS = ['re-arqui.pt', 'www.re-arqui.pt', 'localhost', '127.0.0.1', "www.manuelfelix.eu/teste"]

# Database
# Use SQLite database in production for simplicity
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings - balanced for functionality
# These settings provide security without breaking local development
CSRF_COOKIE_SECURE = False  # Set to True only when HTTPS is properly configured
SESSION_COOKIE_SECURE = False  # Set to True only when HTTPS is properly configured
SECURE_SSL_REDIRECT = False  # Set to True only when HTTPS is properly configured

# Add security headers that don't require HTTPS
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
SECURE_BROWSER_XSS_FILTER = True  # Enable XSS protection in browsers

# FastAPI settings
FASTAPI_PORT = 8001

# Improved logging with console output for better debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django_prod.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
} 