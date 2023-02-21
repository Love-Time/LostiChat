import os
from celery import Celery
from celery.schedules import crontab

from config import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'clearing-code': {
        'task': 'users.tasks.clearing_code',
        'schedule': crontab(minute=f'*/{settings.CODE_LIFE_SECONDS/60}')
    }
}


