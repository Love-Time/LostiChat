from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Create your views here.
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .models import Friends
from .permissions import IsOwner, IsFriend
from .serializers import FriendSerializer, FriendCreateSerializer, FriendRequestSerializer


def contains(lst, filter):
    for x in lst:
        if filter(x):
            print(True)
            return True
    return False


class FriendViewSet(mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):
    serializer_class = FriendSerializer
    queryset = Friends.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'second_user'

    def get_queryset(self):
        if self.action == "requests":
            return Friends.objects.filter(Q(second_user_id=self.request.user.pk) & Q(accepted=0))
        elif self.action == 'list':
            return Friends.objects.filter(Q(first_user_id=self.request.user.id) & Q(accepted=1))
        return Friends.objects.filter(Q(first_user_id=self.request.user.pk) | Q(second_user_id=self.request.user.pk))

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsOwner()]
        elif self.request.method == 'PATCH':
            return [IsFriend()]
        else:
            return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return FriendCreateSerializer
        elif self.action == 'requests':
            return FriendRequestSerializer
        return FriendSerializer

    @action(detail=False, methods=['get'])
    def requests(self, request):
        data = self.get_queryset()
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def denied(self, request, second_user=None):
        obj = get_object_or_404(Friends, Q(first_user_id=second_user) & Q(second_user_id=request.user.pk))
        obj.accepted = -1
        obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def user(self, request, second_user=None):
        data = Friends.objects.filter(Q(first_user_id=second_user) & Q(accepted=1))
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)
