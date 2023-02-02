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
channel_layer = get_channel_layer()
User = get_user_model()


class DialogMessageConsumer(mixins.CreateModelMixin,
                            ObserverModelInstanceMixin,
                            GenericAsyncAPIConsumer):
    queryset = Dialog.objects.all()
    serializer_class = DialogSerializer
    lookup_field = "recipient"

    async def connect(self):
        await self.channel_layer.group_add(f'recipient_{self.scope["user"].id}', self.channel_name)
        await super(DialogMessageConsumer, self).connect()


    @action()
    async def create_dialog_message(self, message, recipient, **kwargs):
        recip = await database_sync_to_async(get_object_or_404)(User, pk=recipient)

        response = await database_sync_to_async(Dialog.objects.create)(
            sender=self.scope["user"],
            recipient=recip,
            message=message
        )
        serializer = DialogSerializer(response)
        async_to_sync(channel_layer.group_send)(f'recipient_{response.recipient.pk}', {"type":"send.message", "data": serializer.data})
        return serializer.data, status.HTTP_200_OK

    def send_message(self, event):
        print(456864384648754875457, event)



    @model_observer(Dialog)
    async def dialog_activity(self, message, observer=None, **kwargs):
        await self.send_json(message)

    @dialog_activity.groups_for_signal
    def dialog_activity(self, instance: Dialog, **kwargs):
        yield f'recipient__{instance.recipient}'
        yield f'pk__{instance.pk}'

    @dialog_activity.groups_for_consumer
    def dialog_activity(self):
        yield f'recipient__{self.scope["user"]}'

    @dialog_activity.serializer
    def dialog_activity(self, instance: Dialog, action, **kwargs):
        return dict(data=DialogSerializer(instance).data, action=action.value, pk=instance.pk)
