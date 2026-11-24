"""
Root WSGI wrapper for chicken_project.
Allows WSGI servers (Gunicorn, uWSGI) to be invoked directly from the root repository directory.
"""
import os
import sys
from pathlib import Path

# Add chicken_project directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
CHICKEN_DIR = BASE_DIR / 'chicken_project'
if str(CHICKEN_DIR) not in sys.path:
    sys.path.insert(0, str(CHICKEN_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chicken_project.settings')

from chicken_project.wsgi import application
