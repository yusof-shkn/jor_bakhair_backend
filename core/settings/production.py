# my_project/settings/prod.py
from .base import *

DEBUG = False

ALLOWED_HOSTS = ["yourdomain.com"]
CORS_ALLOWED_ORIGINS = [
    FRONTEND_DOMAIN,
]
# Production-specific settings