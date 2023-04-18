from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from .models import Code, CustomUser, Settings
from .service import send_activation_email

from .tasks import send_activation_code
from config.settings import EMAIL_HOST_USER


@receiver(post_save, sender=Code)
def create_user_channel(sender, instance, created, **kwargs):
    if EMAIL_HOST_USER:
        text_content = 'This is an important message.'
        html_content = render_to_string('mail.html', {'email': instance.email, 'code': instance.code})
        send_activation_code.delay(text_content, html_content, instance.email, instance.code)

@receiver(post_save, sender=CustomUser)
def create_user_channel(sender, instance, created, **kwargs):
    if created:
        Settings.objects.create(user=instance)
@receiver(post_save, sender=CustomUser)
def save_user_channel(sender, instance, **kwargs):
    instance.channel.save()
