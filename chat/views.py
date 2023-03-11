import math

from django.db.models import Q, QuerySet
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from .permissions import *
from .serializers import *


# Create your views here.

class DuoConversationViewSet(mixins.RetrieveModelMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    queryset = Conversation.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(members=self.request.user, type="duo")


class DialogMessageLastList(mixins.ListModelMixin,
                            GenericViewSet):
    queryset = Dialog.objects.all()
    serializer_class = DialogSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Dialog.objects.raw(f'SELECT *, max(time) \
                                        FROM {Dialog._meta.db_table} \
                                        WHERE sender_id = {self.request.user.id} OR \
                                              recipient_id = {self.request.user.id}\
                                        GROUP BY sender_id, recipient_id \
                                        ORDER BY time DESC')
        message = list(queryset)
        len_message = len(message)
        black_list = [None] * (math.ceil(len_message) + 1)
        len_black_list = 0

        k = 0
        for i in range(len_message):
            if {message[k].sender, message[k].recipient} not in black_list:
                black_list[len_black_list] = {message[k].sender, message[k].recipient}
                len_black_list += 1
                k += 1
                continue
            del message[k]

        return message

class DialogMessagePagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = "page_size"
    max_page_size = 200
class DialogMessageViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           GenericViewSet):
    serializer_class = DialogSerializer
    queryset = Dialog.objects.all()
    permission_classes = (IsAuthenticated, IsOwner)
    pagination_class = DialogMessagePagination

    def get_queryset(self):
        return Dialog.objects.filter(Q(recipient=self.request.user) | Q(sender=self.request.user))

    def get_serializer_class(self):
        if self.action == "create":
            return DialogCreateSerializer
        return DialogSerializer


class DialogApiView(APIView, DialogMessagePagination):

    def get(self, request, pk):
        queryset = Dialog.objects.filter(Q(sender_id=self.request.user.id) & Q(recipient_id=pk) |
                                         Q(sender_id=pk) & Q(recipient_id=self.request.user.id))
        data = self.paginate_queryset(queryset, request, view=self)
        serializer = DialogSerializer(data, many=True, context={'request': request})


        return self.get_paginated_response(serializer.data)
