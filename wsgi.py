"""
Root WSGI wrapper for chicken_project.
Allows WSGI servers (Gunicorn, uWSGI, Vercel) to be invoked directly from the root repository directory.
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

# On Vercel serverless cold-start, auto-apply migrations if connected to an external database
if os.environ.get('VERCEL') and (
    os.environ.get('DATABASE_URL')
    or os.environ.get('POSTGRES_URL')
    or os.environ.get('POSTGRES_PRISMA_URL')
    or os.environ.get('POSTGRES_URL_NON_POOLING')
    or os.environ.get('POSTGRES_HOST')
):
    try:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
    except Exception as e:
        print(f"Auto-migration notice: {e}")
