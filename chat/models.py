from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.
User = get_user_model()


class Conversation(models.Model):
    TYPE = (
        ('duo', "Дуэт"),
        ('multi', "Беседа"))

    type = models.CharField(choices=TYPE, max_length=5, default='', verbose_name="Тип")
    name = models.CharField(max_length=24, blank=True, null=True, verbose_name="Название")
    last_message = models.TextField(blank=True, null=True, verbose_name="Последнее сообщение", )
    members = models.ManyToManyField(User, related_name='members', verbose_name="Участники")
    messages = models.ManyToManyField(User, through="Message", related_name='conv', blank=True)


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='message')
    message = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-time',)
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        constraints = [
            models.UniqueConstraint(
                fields=['sender', 'conversation'], name='unique_migrationMessage_sender_conversation'
            )
        ]
class Forward(models.Model):
    this_message = models.ForeignKey("Dialog", on_delete=models.CASCADE, related_name='this_message')
    other_message = models.ForeignKey("Dialog", on_delete=models.CASCADE, related_name='other_messages')



class Dialog(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_duo')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient_duo')
    message = models.TextField(blank=True, null=True, max_length=4000)
    read = models.BooleanField(default=0)
    time = models.DateTimeField(auto_now_add=True)

    answer = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    forward = models.ManyToManyField('self', null=True, blank=True, through="Forward")
    image = models.ManyToManyField()
    def clean(self):
        if self.answer and self.forward:
            raise ValidationError("Так делать нельзя, либо пересылай сообщения, либо отвечай")
        if not self.message and not self.forward and not self.images:
            raise ValidationError("Сообщение не может быть пустым, проверьте поля forward и message")


        super().clean()

    class Meta:
        ordering = ('-time',)

class Image(models.Model):
    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="chat/image/%Y/%m/%d/", null=True, blank=True)

