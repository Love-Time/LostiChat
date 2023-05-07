import os
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        from users.models import Settings
        Settings.objects.filter(online__gt=0).update(online=0)


