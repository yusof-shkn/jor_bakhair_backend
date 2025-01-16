# my_project/settings/dev.py
from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

CORS_ALLOWED_ORIGINS = [
    FRONTEND_DOMAIN,
]
CSRF_TRUSTED_ORIGINS = [
    FRONTEND_DOMAIN,
]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
ACCESS_CONTROL_ALLOW_CREDENTIALS = True
INSTALLED_APPS += [
    "debug_toolbar",
    "sslserver",
]

# MIDDLEWARE += [
#     "debug_toolbar.middleware.DebugToolbarMiddleware",
# ]
INTERNAL_IPS = [
    "127.0.0.1",
    "192.168.*.*",
]
