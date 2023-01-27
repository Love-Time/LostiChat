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
    recipient = UserSimpleSerializer(read_only=True)
    class Meta:
        model = Dialog
        fields = "__all__"
        read_only_fields = ['sender', 'recipient', 'time']


