from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from rest_framework import status
from .models import Dialog
from config.settings import EMAIL_HOST_USER
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
        serializer = DialogSerializer(instance, context={'request': {'user': instance.sender}})
        async_to_sync(channel_layer.group_send)(f'recipient_{instance.recipient.pk}',
                                           {"type": "send_message", "data": serializer.data})
