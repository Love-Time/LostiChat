"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from asgiref.sync import sync_to_async

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.core.asgi import get_asgi_application
from users.service import do_default_online_users


from . import routing
from config.middleware import TokenAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# application = get_asgi_application()
print(URLRouter(routing.websocket_urlpatterns))
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket' : TokenAuthMiddleware(
        URLRouter(routing.websocket_urlpatterns)
    )
})