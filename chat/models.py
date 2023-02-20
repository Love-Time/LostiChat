from django.contrib.auth import get_user_model
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

class Dialog(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_duo')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient_duo')
    message = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ('-time',)


