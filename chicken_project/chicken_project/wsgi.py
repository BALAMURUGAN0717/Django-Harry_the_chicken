"""
WSGI config for chicken_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Ensure chicken_project directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chicken_project.settings')

application = get_wsgi_application()

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
