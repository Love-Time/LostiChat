import json

from asgiref.sync import sync_to_async, async_to_sync
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djangochannelsrestframework import mixins
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer import model_observer
from rest_framework import status
from rest_framework.response import Response

from .models import Friends

from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser

from .serializers import FriendSerializer

channel_layer = get_channel_layer()
User = get_user_model()
import socket


class FriendConsumer(ObserverModelInstanceMixin,
                            GenericAsyncAPIConsumer):
    queryset = Friends.objects.all()
    serializer_class = FriendSerializer


    async def connect(self):
        self.user = self.scope['user']
        print(socket.gethostname(), 'socket hostname')
        if self.scope['user'] != AnonymousUser():
            await self.channel_layer.group_add(f'friend_{self.scope["user"].id}', self.channel_name)

            await self.accept()
        else:
            await self.close(code=401)



    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            f'friend_{self.scope["user"].id}',
            self.channel_name
        )
        await super().disconnect(code)




    @action()
    async def add_friend(self, user_pk):
        recip_user = get_object_or_404(User, pk=user_pk)

        my_request_to_friend = Friends.objects.filter(first_user=self.user, second_user=recip_user)
        if my_request_to_friend:
            return {
                'type': 'exist',
                'messgae': "The friend request has already been sent"
            }, status.HTTP_200_OK

        my_request_to_friend = Friends.objects.create(first_user=self.user, second_user=recip_user)

        if my_request_to_friend.accepted==1:
            #Заявка принята, ещё здесь надо отправить сообщение второму пользователю
            return {
                'type': 'accepted',
                'message': "You have accepted the request as a friend"
            }



        other_request_to_friend =  Friends.objects.filter(first_user=recip_user, second_user=self.user)
    @action()
    async def create_dialog_message(self, message, recipient, **kwargs):
        recip = await database_sync_to_async(get_object_or_404)(User, pk=recipient)

        response = await database_sync_to_async(Dialog.objects.create)(
            sender=self.scope["user"],
            recipient=recip,
            message=message
        )
        serializer = DialogSerializer(response, context={'request': self.scope})
        if response.recipient.pk!=self.user.pk:
            await channel_layer.group_send(f'recipient_{response.recipient.pk}',
                                        {"type": "send_message", "data": serializer.data})

        return serializer.data, status.HTTP_200_OK

    async def send_message(self, event):
        await self.send_json(
            {
                'data': event['data'],
                'status': status.HTTP_200_OK,
                'action': "receiving_message"
            }
        )
