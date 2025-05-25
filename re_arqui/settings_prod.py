"""
Production Django settings for re_arqui project.
"""

from pathlib import Path
import os
import json

# Import base settings
from .settings import *

# Production-specific paths
PROD_STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_prod')
PROD_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_prod')

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
DEBUG = False

# Updated to include both domains
ALLOWED_HOSTS = [
    're-arqui.pt',
    'www.re-arqui.pt',
    'manuelfelix.eu',
    'www.manuelfelix.eu',
    'localhost',
    '127.0.0.1'
]

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
STATIC_ROOT = PROD_STATIC_ROOT  # Production static files
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # Enable static files directory

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = PROD_MEDIA_ROOT  # Production media files

# Update middleware for production
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Add WhiteNoise static files storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Security settings
CSRF_COOKIE_SECURE = False  # Temporarily disabled for local testing
SESSION_COOKIE_SECURE = False  # Temporarily disabled for local testing
SECURE_SSL_REDIRECT = False  # Temporarily disabled for local testing
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Additional security headers
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# FastAPI settings
FASTAPI_PORT = 8001

# Improved logging with more detailed output
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'gunicorn': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
} 