from django.shortcuts import get_object_or_404
from rest_framework import serializers

from users.serializers import UserSimpleSerializer
from .models import *
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
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


class AnswerDialogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dialog
        exclude = ['answer', 'forward']

class ForwardDialogSerializer(serializers.ModelSerializer):
    sender = UserSimpleSerializer()
    class Meta:
        model = Dialog
        exclude = ['recipient', 'answer']
class DialogSerializer(serializers.ModelSerializer):
    sender = UserSimpleSerializer(read_only=True)
    recip = UserSimpleSerializer(source='recipient', read_only=True)
    answer = AnswerDialogSerializer()
    forward = ForwardDialogSerializer(many=True, read_only=True)


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
    forward = ForwardDialogSerializer(many=True, read_only=True)
    def validate(self, data):
        if data.get('answer', ""):
            if {data['sender'], data['recipient']} != {data['answer'].sender, data['answer'].recipient}:
                raise ValidationError("Наебать не получится, выбери сообщение из своего чата")

        return data

    def create(self, validated_data):
        obj = Dialog.objects.create(**validated_data)
        print("ffffgfgfgfg", self.initial_data)
        if self.initial_data.get('forward', ""):
            print( )
            for message in self.initial_data['forward']:
                obj.forward.add(get_object_or_404(Dialog, pk=message), through_defaults={'this_message': obj})
        obj.save()
        return obj
    class Meta:
        model = Dialog
        fields = "__all__"
        extra_kwargs = {
            'recipient': {'write_only': True}
        }




