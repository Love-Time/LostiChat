import asyncio
import json
import socket
import time

from asgiref.sync import sync_to_async, async_to_sync
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djangochannelsrestframework import mixins
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer import model_observer
from rest_framework import status
from rest_framework.response import Response

from users.models import Settings
from .models import Dialog
from .serializers import DialogSerializer, DialogCreateSerializer
from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser

channel_layer = get_channel_layer()
User = get_user_model()

class myRequest():
    def __init__(self, user):
        self.user = user


class DialogMessageConsumer(mixins.CreateModelMixin,
                            ObserverModelInstanceMixin,
                            GenericAsyncAPIConsumer):
    queryset = Dialog.objects.all()
    serializer_class = DialogCreateSerializer
    lookup_field = "recipient"

    async def connect(self):
        self.user = self.scope['user']
        if self.scope['user'] != AnonymousUser():
            await self.channel_layer.group_add(f'recipient_{self.scope["user"].id}', self.channel_name)
            await self.accept()
            self.queue = []
            self.__start = False

            #online+=1
            user_settings = await sync_to_async(Settings.objects.get)(user=self.scope['user'])
            user_settings.online = user_settings.online + 1
            await sync_to_async(user_settings.save)()
        else:
            await self.close(code=401)


    async def disconnect(self, code):
        if self.scope['user'] != AnonymousUser():
            user_settings = await sync_to_async(Settings.objects.get)(user=self.scope['user'])
            user_settings.online = user_settings.online - 1
            await sync_to_async(user_settings.save)()

        await self.channel_layer.group_discard(
            f'recipient_{self.scope["user"].id}',
            self.channel_name
        )
        await super().disconnect(code)

    async def do_queue(self):
        self.__start = True
        while self.queue:
            await sync_to_async(self.create_dialog_message2)(message=self.queue[0][1]['message'],
                                                                        recipient=self.queue[0][1]['recipient'],
                                                                        request_id=self.queue[0][1]['request_id'],
                                                                        action=self.queue[0][1].get('action',""),
                                                                        forward= self.queue[0][1].get('forward', ""),
                                                                        answer=self.queue[0][1].get('answer', ""))

            # await channel_layer.group_send(f'recipient_{instance["sender"]["pk"]}',
            #                                         {"type": "send_message", "data": instance})
            del self.queue[0]
            await asyncio.sleep(1)
        self.__start = False

    @action()
    async def create_dialog_message(self, **kwargs):
        self.queue.append((self.create_dialog_message, kwargs))
        print('start')

        if not self.__start:
            asyncio.create_task(self.do_queue())

    def create_dialog_message2(self, **kwargs):
        #recip = await database_sync_to_async(get_object_or_404)(User, pk=recipient)

        serializer = DialogCreateSerializer(data=kwargs, context= {'request': myRequest(self.scope['user'])})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, **kwargs)





    async def send_message(self, event):
        await self.send_json(
            {
                'data': event['data'],
                'status': status.HTTP_200_OK,
                'action': "receiving_message"
            }
        )

    async def send_friend(self, event):
        await self.send_json(
            {
                'data': event['data'],
                'status': status.HTTP_200_OK,
                'action': "friend"
            }
        )


    # @model_observer(Dialog)
    # async def dialog_activity(self, message, observer=None, **kwargs):
    #     await self.send_json(message)
    #
    # @dialog_activity.groups_for_signal
    # def dialog_activity(self, instance: Dialog, **kwargs):
    #     yield f'recipient__{instance.recipient}'
    #     yield f'pk__{instance.pk}'
    #
    # @dialog_activity.groups_for_consumer
    # def dialog_activity(self):
    #     yield f'recipient__{self.scope["user"]}'
    #
    # @dialog_activity.serializer
    # def dialog_activity(self, instance: Dialog, action, **kwargs):
    #     return dict(data=DialogSerializer(instance).data, action=action.value, pk=instance.pk)
