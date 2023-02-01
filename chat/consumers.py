from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djangochannelsrestframework import mixins
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer import model_observer

from .models import Dialog
from .serializers import DialogSerializer
from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)

User = get_user_model()


class DialogMessageConsumer(mixins.CreateModelMixin,
                            ObserverModelInstanceMixin,
                            GenericAsyncAPIConsumer):
    queryset = Dialog.objects.all()
    serializer_class = DialogSerializer
    lookup_field = "recipient"

    @action()
    async def create_dialog_message(self, message, recipient, **kwargs):
        a = await database_sync_to_async(Dialog.objects.create)(
            sender=self.scope["user"],
            recipient=sync_to_async(get_object_or_404)(User, pk=recipient),
            message=message
        )
        sync_to_async(print)('a', a)

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
