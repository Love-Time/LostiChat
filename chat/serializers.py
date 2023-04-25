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
    sender = UserSimpleSerializer()
    recipient = UserSimpleSerializer()
    class Meta:
        model = Dialog
        exclude = ['answer', 'forward']

class ForwardDialogSerializer(serializers.ModelSerializer):
    sender = UserSimpleSerializer()
    forward = serializers.SerializerMethodField()

    def get_forward(self, data):
        if data.forward.all():
            return ForwardDialogSerializer(data.forward, many=True).data
        else:
            return []
    class Meta:
        model = Dialog
        exclude = ['recipient', 'answer']




class DialogSerializer(serializers.ModelSerializer):
    sender = UserSimpleSerializer(read_only=True)
    recip = UserSimpleSerializer(source='recipient', read_only=True)
    answer = AnswerDialogSerializer()
    forward = ForwardDialogSerializer(many=True, read_only=True)
    images = serializers.SerializerMethodField()

    def get_images(self, data):
        images = list(data.image_set.all())
        images = [image.id for image in images]
        return images



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
    answer = AnswerDialogSerializer(read_only=True)
    def validate(self, data):
        print("first first first ", data.get('answer', ""))
        if data.get('answer', ""):
            if {data['sender'], data['recipient']} != {data['answer'].sender, data['answer'].recipient}:
                raise ValidationError("Наебать не получится, выбери сообщение из своего чата")
            print("i am here 3434343434")
            if not data.get('message', ""):
                print("why not&&&&&&&&&&&&&&&&&&&&&&&&&&&&", data.get('message', ""))
                raise ValidationError("Ну ты болван, напиши хоть что-нибудь")
        return data

    def create(self, validated_data):
        obj = Dialog.objects.create(**validated_data)
        if self.initial_data.get('forward', ""):
            all_forward = [Forward(this_message_id=obj.id, other_message_id=message_id) for message_id in self.initial_data['forward']]
            Forward.objects.bulk_create(
                all_forward
            )
        elif self.initial_data.get('answer', ""):
            obj.answer_id = self.initial_data.get('answer', "")
        obj.save()
        return obj
    class Meta:
        model = Dialog
        fields = "__all__"
        extra_kwargs = {
            'recipient': {'write_only': True}
        }




