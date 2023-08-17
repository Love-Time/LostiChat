from django.core.mail import EmailMultiAlternatives
from users.models import Settings

def send_activation_email(content, html, email, code):
    sendMail(text_content=content,
             html_content=html,
             to=[email])


def sendMail(subject="Тема Письма", text_content="Сообщение", html_content=None, to: list = None):
    message = EmailMultiAlternatives(subject, text_content, to=to)
    message.mixed_subtype = 'related'
    message.attach_alternative(html_content, "text/html")
    message.send()


def do_default_online_users():
    settings = Settings.objects.filter(online__gt=0).update(online=0)
    settings.update(online=0)
