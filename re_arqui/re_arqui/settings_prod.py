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
with open(os.path.join(BASE_DIR, 'secret_key.json')) as f:
    SECRET_KEY = json.load(f)['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['re-arqui.pt', 'www.re-arqui.pt']

# Database
# Use MySQL database in production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rearqui_db',
        'USER': 'rearqui_dbuser',
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),  # Set this in the production environment
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'sql_mode': 'STRICT_TRANS_TABLES',
        }
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# HTTPS settings
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# FastAPI settings - use a different port for production
FASTAPI_PORT = 8001

# Logging
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
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django_prod.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
} 