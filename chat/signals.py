from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework import status

from users.service import do_default_online_users
from .models import Dialog
from .serializers import DialogSerializer


def send_message(self, event):
    async_to_sync(
        self.send_json(
            {
                'data': event['data'],
                'status': status.HTTP_200_OK,
                'action': "receiving_message"
            }
        ))


channel_layer = get_channel_layer()


@receiver(post_save, sender=Dialog)
def send_message(sender, instance, created, **kwargs):
    if created:
        serializer = DialogSerializer(instance)
        print(serializer.data)
        async_to_sync(channel_layer.group_send)(f'recipient_{instance.recipient.pk}',
                                                {"type": "send_message", "data": serializer.data})
