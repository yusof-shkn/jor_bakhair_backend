"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from core.settings.base import DEVELOPMENT
from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core.settings.development" if DEVELOPMENT else "core.settings.production",
)  # Change to prod for production

application = get_wsgi_application()
