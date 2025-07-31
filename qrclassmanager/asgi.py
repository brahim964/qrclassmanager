"""
ASGI config for qrclassmanager project.
Expone la variable ``application`` a los servidores ASGI.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qrclassmanager.settings")

application = get_asgi_application()
