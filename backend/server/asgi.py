import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from apps.executions import routing as executions_routing
from apps.collaboration import routing as collaboration_routing
from apps.notifications import routing as notifications_routing
from apps.executions.middleware import JWTAuthMiddleware

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(
        URLRouter(
            executions_routing.websocket_urlpatterns +    
            collaboration_routing.websocket_urlpatterns +
            notifications_routing.websocket_urlpatterns
        )
    ),
})