from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from .models import Code


def sendMail(subject="Тема Письма", text_content="Сообщение", html_content=None, to: list = None):
    message = EmailMultiAlternatives(subject, text_content, to=to)
    message.mixed_subtype = 'related'
    message.attach_alternative(html_content, "text/html")
    message.send()


@receiver(post_save, sender=Code)
def create_user_channel(sender, instance, created, **kwargs):
    text_content = 'This is an important message.'
    html_content = render_to_string('mail.html', {'instance': instance})

    sendMail(text_content=text_content,
             html_content=html_content,
             to=[instance.email])
