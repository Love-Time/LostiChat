from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from users.serializers import UserSimpleSerializer
from .models import Friends


class FriendSerializer(serializers.ModelSerializer):
    first_user = UserSimpleSerializer(write_only=True, default=CurrentUserDefault())
    friend = UserSimpleSerializer(source='second_user')
    class Meta:
        model = Friends
        exclude = ['second_user']
