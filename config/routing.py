from django.urls import path, include
from djangochannelsrestframework import consumers
from chat.routing import websocket_urlpatterns as urlpatterns_chat
from friends.routing import websocket_urlpatterns as urlpatterns_friends


websocket_urlpatterns = [
    *urlpatterns_chat,
    *urlpatterns_friends

]