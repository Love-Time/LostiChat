from django.urls import path

from chat import consumers

websocket_urlpatterns = [
    path('ws/chat/', consumers.DialogMessageConsumer.as_asgi()),
]