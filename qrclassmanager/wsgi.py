"""
WSGI config for qrclassmanager project.
Expone la variable ``application`` a los servidores WSGI/Docker‑gunicorn, etc.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qrclassmanager.settings")

application = get_wsgi_application()
