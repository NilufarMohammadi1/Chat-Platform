from .wsgi import *
from channels.routing import ProtocolTypeRouter, URLRouter

from django.urls import include, re_path
# from django.conf.urls import url
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator,OriginValidator
from Chats.consumers import ChatConsumer

application = ProtocolTypeRouter({
    #whaaaaaat
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    re_path(r'^messages/$', ChatConsumer.as_asgi()),
                    re_path(r'^messages/(?P<thread_id>[\w.@+-]+)', ChatConsumer.as_asgi()),
                    # re_path(r"^messages/(?P<username>[\w.@+-]+)", ChatConsumer.as_asgi()),
                    # re_path("messages/<str:username>", ChatConsumer.as_asgi()),
                ]
            )
    ))
})
