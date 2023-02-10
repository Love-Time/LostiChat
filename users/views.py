from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from .models import CustomUser
from .permissions import IsOwner
from .serializers import *


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsOwner,)

class UserSimpleList(mixins.ListModelMixin,
                     GenericViewSet):
    serializer_class = UserSimpleSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.exclude(pk=self.request.user.pk)

