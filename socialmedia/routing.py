from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path

from chat import routing as chat_routing
from chat.consumers import ChatConsumer

print(chat_routing.websocket_urlpatterns)
application = ProtocolTypeRouter({
    'websocket': URLRouter([
        path('ws/chat/<str:chat_id>/', ChatConsumer.as_asgi()),
    ])
})
