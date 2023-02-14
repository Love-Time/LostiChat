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
from .serializers import FriendSerializer


def contains(lst, filter):
    for x in lst:
        if filter(x):
            print(True)
            return True
    return False


class FriendViewSet(ModelViewSet):
    serializer_class = FriendSerializer
    queryset = Friends.objects.all()
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        if self.action == "requests":
            return Friends.objects.filter(Q(second_user_id=self.request.user.pk) & Q(accepted=False))
        return Friends.objects.filter(Q(first_user_id=self.request.user.pk) | Q(second_user_id=self.request.user.pk))

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsOwner()]
        elif self.request.method == 'PATCH':
            return [IsFriend()]
        else:
            return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        data = list(self.get_queryset())

        me, another = [], []
        for x in data:
            (me, another)[x.first_user.pk != request.user.pk].append(x)

        len_me = len(me) - 1
        for i in range(len_me, -1, -1):

            if not contains(another, lambda x: x.first_user.pk == me[i].second_user.pk and
                                               x.second_user.pk == me[i].first_user.pk):
                del me[i]

        serializer = self.get_serializer(me, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def requests(self, request):
        data = self.get_queryset()
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def denied(self, request, pk=None):
        obj = get_object_or_404(Friends, Q(second_user=request.user) & Q(first_user_id=pk))
        obj.accepted = -1
        obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
