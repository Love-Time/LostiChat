from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Create your views here.
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from users.serializers import UserSimpleSerializer
from .models import Friends
from .permissions import IsOwner, IsFriend
from .serializers import FriendSerializer, FriendCreateSerializer, FriendRequestSerializer, PossibleFriendsSerializer

User = get_user_model()

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

    @action(detail=False, methods=['get'])
    def possible_friends(self, request):
        me_friends = list(Friends.objects.filter(Q(first_user=self.request.user) & Q(accepted=1)))
        for i in range(len(me_friends)):
            me_friends[i] = me_friends[i].second_user

        possible_friends = Friends.objects.filter(Q(first_user__in=me_friends) & Q(accepted=1)) \
            .exclude(Q(second_user__in=me_friends) | Q(second_user=request.user)).values("second_user").annotate(count=Count('second_user')).order_by('-count')
        serializer = PossibleFriendsSerializer(possible_friends, many=True)
        return Response(serializer.data)

    # @action(detail=False, methods=['get'])
    # def possible_friends(self, request):
    #     me_friends = list(Friends.objects.filter(Q(first_user=self.request.user) & Q(accepted=1)))
    #     for i in range(len(me_friends)):
    #         me_friends[i] = me_friends[i].second_user
    #
    #     possible_friends = list(Friends.objects.filter(Q(first_user__in=me_friends) & Q(accepted=1)) \
    #         .exclude(Q(second_user__in=me_friends) | Q(second_user=request.user)).order_by('second_user'))
    #     if possible_friends:
    #         user_id = None
    #         new_data = []
    #         for i in range(len(possible_friends)):
    #             if user_id != possible_friends[i].second_user_id:
    #                 new_dict = {'possible_friend': UserSimpleSerializer(possible_friends[i].second_user).data,
    #                             'friends': [UserSimpleSerializer(possible_friends[i].first_user).data]}
    #                 new_data.append(new_dict)
    #                 user_id = possible_friends[i].second_user_id
    #                 continue
    #
    #             new_data[-1]['friends'].append(UserSimpleSerializer(possible_friends[i].first_user).data)
    #
    #         for i in range(len(new_data)):
    #             new_data[i]['count'] = len(new_data[i]['friends'])
    #
    #         new_data = sorted(new_data, key=lambda d: d['count'])
    #
    #         #serializer = SimpleSerializer(possible_friends, many=True)
    #         return Response(new_data)
    #
    #     data = list(User.objects.exclude(Q(pk__in=self.request.user.pk) | Q(pk__in=me_friends)))
    #     new_data = []
    #     for i in range(len(data)):
    #         obj = {'possible_friend': UserSimpleSerializer(data[i]).data, 'friends': [], 'count': 0}
    #         new_data.append(obj)
    #     return Response(new_data)




