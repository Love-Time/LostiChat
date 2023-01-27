import math

from django.db.models import Q, QuerySet
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
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
        black_list = [None] * math.ceil(len_message/2)
        len_balck_list = 0
        for i in range(len_message):
            if {message[i].sender, message[i].recipient} not in black_list:
                black_list[len_balck_list] = {message[i].sender, message[i].recipient}
                len_balck_list+=1
                continue
            del message[i]
            i-=1

        return message

class DialogMessageViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    serializer_class = DialogSerializer
    queryset = Dialog.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOrReadonly)

    def get_queryset(self):
        return Dialog.objects.filter(Q(recipient=self.request.user) | Q(sender=self.request.user))

    def get_serializer_class(self):
        if self.action == "create":
            return DialogCreateSerializer
        return DialogSerializer

class DialogApiView(APIView):
    def get(self,request, pk):
        queryset = Dialog.objects.filter(Q(sender_id=self.request.user.id) & Q(recipient_id=pk)  |
                                         Q(sender_id=pk) & Q(recipient_id=self.request.user.id))
        serializer = DialogSerializer(queryset, many=True)
        return  Response(serializer.data)
