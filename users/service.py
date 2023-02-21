from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_activation_email(content, html, email, code):
    text_content = 'This is an important message.'
    html_content = render_to_string('mail.html', {'email': email, 'code': code})

    sendMail(text_content=content,
             html_content=html,
             to=[email])

def sendMail(subject="Тема Письма", text_content="Сообщение", html_content=None, to: list = None):

    message = EmailMultiAlternatives(subject, text_content, to=to)
    message.mixed_subtype = 'related'
    message.attach_alternative(html_content, "text/html")
    message.send()