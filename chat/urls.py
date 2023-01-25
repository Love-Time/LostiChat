from django.urls import path, include, re_path
from . import views
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'conversation', DuoConversationViewSet)


urlpatterns = [
    path('api/v1/', include(router.urls)),
]