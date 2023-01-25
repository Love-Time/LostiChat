import math

from django.db.models import Q, QuerySet
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

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

class MessageDialogViewSet(ModelViewSet):
    queryset = Dialog.objects.all()
    serializer_class = DialogSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        queryset = Dialog.objects.raw('SELECT *, max(time) FROM "chat_messageduo" WHERE ("chat_messageduo"."sende\
r_id" = 1 OR "chat_messageduo"."recipient_id" = 1) GROUP BY sender_id, recipient_id ORDER BY time DESC')
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

