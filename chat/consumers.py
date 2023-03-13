import asyncio
import json
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

from .models import Dialog
from .serializers import DialogSerializer
from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser

channel_layer = get_channel_layer()
User = get_user_model()


def retry(func):
    async def _wrapper(self, *args, **kwargs):
        self.queue.append((func, args, kwargs))
        if not self.__start:
            yield

    return _wrapper
class DialogMessageConsumer(mixins.CreateModelMixin,
                            ObserverModelInstanceMixin,
                            GenericAsyncAPIConsumer):
    queryset = Dialog.objects.all()
    serializer_class = DialogSerializer
    lookup_field = "recipient"

    async def connect(self):
        self.user = self.scope['user']
        if self.scope['user'] != AnonymousUser():
            await self.channel_layer.group_add(f'recipient_{self.scope["user"].id}', self.channel_name)
            await self.accept()
            self.queue = []
            self.__start = False
        else:
            await self.close(code=401)


    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            f'recipient_{self.scope["user"].id}',
            self.channel_name
        )
        await super().disconnect(code)

    async def start_queue(self):
        self.__start = True
        while self.queue:
            print(self.queue)
            instance, data = await self.create_dialog_message2(message=self.queue[0][2]['message'], recipient=self.queue[0][2]['recipient'], request_id=self.queue[0][2]['request_id'], action=self.queue[0][2]['action'])
            await channel_layer.group_send(f'recipient_{instance.sender.pk}',
                                                    {"type": "send_message", "data": data})
            del self.queue[0]
            print("СПАТЬ")
            time.sleep(5)
        print('закончили')
        self.__start = False
    @staticmethod
    def retry(func):
        async def _wrapper(self, *args, **kwargs):

            self.queue.append((func, args, kwargs))
            if not self.__start:
                print('startuem', self)
                print("ПОЧЕМУ", self.__start)
                await self.start_queue()


        return _wrapper


    @action()
    @retry
    async def create_dialog_message(self, message, recipient, **kwargs):
        recip = await database_sync_to_async(get_object_or_404)(User, pk=recipient)

        response = await database_sync_to_async(Dialog.objects.create)(
            sender=self.scope["user"],
            recipient=recip,
            message=message
        )
        serializer = DialogSerializer(response)

        return serializer.data, status.HTTP_201_CREATED

    async def create_dialog_message2(self, message, recipient, **kwargs):
        print('i am here2')
        recip = await database_sync_to_async(get_object_or_404)(User, pk=recipient)

        response = await database_sync_to_async(Dialog.objects.create)(
            sender=self.scope["user"],
            recipient=recip,
            message=message
        )
        serializer = DialogSerializer(response)

        return response, serializer.data

    async def send_message(self, event):
        await self.send_json(
            {
                'data': event['data'],
                'status': status.HTTP_200_OK,
                'action': "receiving_message"
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
