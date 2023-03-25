from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from rest_framework import status

from users.serializers import UserSimpleSerializer
from .models import Friends



channel_layer = get_channel_layer()


@receiver(post_save, sender=Friends)
def create_user_channel(sender, instance: Friends, created, **kwargs):
    another_request = Friends.objects.filter(first_user=instance.second_user, second_user=instance.first_user)
    serializer = UserSimpleSerializer(instance.first_user)
    if not another_request and instance.accepted == 0:
        # Сказать второму, что ему отправили запрос в друзья
        async_to_sync(channel_layer.group_send)(f'recipient_{instance.second_user.id}',
                                                {"type": "friend_message", "data": {'type': 'friend_request',
                                                                                  'description': "Пришёл запрос в друзья",
                                                                                  'user': serializer.data}})
        return
    if instance.accepted == 1 and another_request == 1:
        # Сказать второму, что его запрос в друзья приняли
        async_to_sync(channel_layer.group_send)(f'recipient_{instance.second_user.id}',
                                                {"type": "friend_message", "data": {'type': 'friend_accepted',
                                                                                  'description': "Запрос в друзья принят",
                                                                                  'user': serializer.data}})
        return
    if instance.accepted == -1 and another_request == 1:
        # Сказать второму, что его запрос отклонили
        async_to_sync(channel_layer.group_send)(f'recipient_{instance.second_user.id}',
                                                {"type": "friend_message", "data": {'type': 'friend_denied',
                                                                                  'description': "Запрос в друзья отклонён",
                                                                                  'user': serializer.data}})
        return


@receiver(pre_delete, sender=Friends)
def create_user_channel(sender, instance: Friends, created, **kwargs):
    another_request = Friends.objects.filter(first_user=instance.second_user, second_user=instance.first_user)
    serializer = UserSimpleSerializer(instance.first_user)
    if not another_request and instance.accepted == 0:
        # Сказать второму, что пользователь передумал отправлять запрос в друзья
        async_to_sync(channel_layer.group_send)(f'recipient_{instance.second_user.id}',
                                                {"type": "friend_message", "data": {'type': 'friend_canceled',
                                                                                  'description': "Запрос в друзья отменён",
                                                                                  'user': serializer.data}})
        return
    if another_request[0].accepted == 1 and instance.accepted == 1:
        # Сказать второму, что его удалили из друзей
        async_to_sync(channel_layer.group_send)(f'recipient_{instance.second_user.id}',
                                                {"type": "friend_message", "data": {'type': 'friend_delete',
                                                                                  'description': "Удалён из друзей",
                                                                                  'user': serializer.data}})
        return
