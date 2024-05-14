import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'happyhours.settings.production')
django.setup()
from apps.order.middleware import JwtAuthMiddlewareStack
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from apps.order import routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
