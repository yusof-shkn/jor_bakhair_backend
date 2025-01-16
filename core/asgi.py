import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import apps.chat.routing
import apps.notifications.routing
from core.settings.base import DEVELOPMENT

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core.settings.development" if DEVELOPMENT else "core.settings.production",
)

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                apps.chat.routing.websocket_urlpatterns
                + apps.notifications.routing.websocket_urlpatterns
            )
        ),
    }
)
