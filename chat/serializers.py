from rest_framework import serializers

from users.serializers import UserSimpleSerializer
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['sender', 'conversation', 'message', 'time']
        read_only_fields = ['sender', 'conversation', 'time']

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        exclude = ['messages']
        read_only_fields = ['type']
class DialogSerializer(serializers.ModelSerializer):
    sender = UserSimpleSerializer(read_only=True)
    recip = UserSimpleSerializer(source='recipient', read_only=True)


    def is_type_user(self, message):
        if isinstance(self.context['request'], dict):
            user = self.context['request']['user']
        else:
            user = self.context['request'].user

        if message.sender.pk == user.pk:
            return "sender"
        else:
            return "recip"

    class Meta:
        model = Dialog
        exclude = ['recipient']

class DialogCreateSerializer(serializers.ModelSerializer):
    sender = UserSimpleSerializer(default=serializers.CurrentUserDefault())
    recip = UserSimpleSerializer(source='recipient', read_only=True)
    class Meta:
        model = Dialog
        fields = "__all__"
        extra_kwargs = {
            'recipient': {'write_only': True}
        }




