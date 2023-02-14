from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from users.serializers import UserSimpleSerializer
from .models import Friends


class FriendSerializer(serializers.ModelSerializer):
    first_user = serializers.HiddenField(write_only=True, default=CurrentUserDefault())
    friend = UserSimpleSerializer(source='second_user')
    class Meta:
        model = Friends
        exclude = ['second_user', 'first_user', 'accepted']

class FriendCreateSerializer(serializers.ModelSerializer):
    first_user = serializers.HiddenField(write_only=True, default=CurrentUserDefault())
    class Meta:
        model = Friends
        exclude = ['accepted']
