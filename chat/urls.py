from django.urls import path, include, re_path
from . import views
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'dialogs', DialogMessageLastList)
router.register(r'dialog/message', DialogMessageViewSet)


urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/dialog/<int:pk>/', DialogApiView.as_view()),
    path('api/v1/dialog/attachments/images/<int:pk>/', AttachmentsImagesView.as_view()),
    path('api/v1/media/chat/image/<int:pk>/', MediaAccess.as_view(), name='media')

]