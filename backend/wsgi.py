"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from .db_backup import restore_database
import subprocess
from pathlib import Path

# Configure Git to use token
BASE_DIR = Path(__file__).resolve().parent.parent
github_token = os.environ.get('GITHUB_TOKEN')
if github_token:
    subprocess.run(['git', 'config', '--global', 'url.https://${GITHUB_TOKEN}@github.com/.insteadOf', 'https://github.com/'], cwd=BASE_DIR)

# Try to restore the database on startup
restore_database()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()
