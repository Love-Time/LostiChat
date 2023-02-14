from django.urls import path, include, re_path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import FriendViewSet

router = routers.DefaultRouter()
router.register(r'friends', FriendViewSet)
print(router.urls)
urlpatterns = [
    path('api/v1/', include(router.urls)),
]