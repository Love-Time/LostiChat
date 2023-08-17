import datetime
from pytz import timezone
from config import settings
from config.celery import app
from .service import send_activation_email
from .models import Code

@app.task
def send_activation_code(content, html, email, code):
    send_activation_email(content, html, email, code)


@app.task
def clearing_code():
    time_zone = timezone(settings.TIME_ZONE)
    time = datetime.datetime.now(time_zone) - datetime.timedelta(seconds=settings.CODE_LIFE_SECONDS)
    Code.objects.filter(time__lte=time).delete()
