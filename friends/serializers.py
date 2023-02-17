from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.validators import UniqueTogetherValidator

from users.serializers import UserSimpleSerializer
from .models import Friends
User = get_user_model()
class PossibleFriendsSerializer(serializers.ModelSerializer):
    possible_friend = serializers.SerializerMethodField('get_user')
    count = serializers.IntegerField()

    def get_user(self, obj):
        print(obj)
        user = User.objects.get(pk=obj['second_user'])
        return UserSimpleSerializer(user).data


    class Meta:
        model=Friends
        fields = ['possible_friend', 'count']

class FriendSerializer(serializers.ModelSerializer):
    friend = UserSimpleSerializer(source='second_user')
    class Meta:
        model = Friends
        exclude = ['second_user', 'first_user', 'accepted']

class FriendCreateSerializer(serializers.ModelSerializer):
    first_user = serializers.HiddenField(write_only=True, default=CurrentUserDefault())

    def validate(self, data):
        if data['first_user'] == data['second_user']:
            raise serializers.ValidationError("You can't add yourself as a friend")
        return data
    class Meta:
        model = Friends
        exclude = ['accepted']

        validators = [
            UniqueTogetherValidator(queryset=Friends.objects.all(),
                                    fields=['first_user', 'second_user'])
        ]

class FriendRequestSerializer(serializers.ModelSerializer):
    friend = UserSimpleSerializer(source="first_user")
    class Meta:
        model = Friends
        fields = ['pk', 'friend']

