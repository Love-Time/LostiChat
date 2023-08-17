from django.urls import path, include, re_path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


from .views import UserSimpleList, UserViewSet, CodeViewSet, SettingsView

router = routers.DefaultRouter()
router.register(r'findPeople', UserSimpleList)

router2 = routers.DefaultRouter()
router2.register("users", UserViewSet)
router2.register("code", CodeViewSet)

urlpatterns = [
    path('api/v1/auth/', include(router2.urls)),
    re_path(r'^auth/', include('djoser.urls.jwt')),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/v1/', include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path("api/v1/auth/users/settings/me/", SettingsView.as_view(), name="settings"),
]

