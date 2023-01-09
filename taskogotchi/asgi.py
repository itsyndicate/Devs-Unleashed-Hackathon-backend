"""
ASGI config for taskogotchi project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
import game.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskogotchi.settings')

application = ProtocolTypeRouter(
    {
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(game.routing.websocket_urlpatterns))
        ),
        "http": get_asgi_application(),
    }
)
