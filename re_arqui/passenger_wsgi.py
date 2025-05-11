import os
import sys

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Set up the Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "re_arqui.settings_prod")

# Import the WSGI application
from re_arqui.wsgi import application