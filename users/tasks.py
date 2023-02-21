from config.celery import app
from .service import send_activation_email


@app.task
def send_activation_code(content, html, email, code):
    send_activation_email(content, html, email, code)
