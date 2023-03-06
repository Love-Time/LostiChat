from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/friend/', consumers.FriendConsumer.as_asgi()),
]