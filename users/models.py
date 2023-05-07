import datetime
from random import randint
from PIL import Image
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.db import models
from pytz import timezone

from config import settings
from config.services import crop_center_v2


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        assert extra_fields['is_staff']
        assert extra_fields['is_superuser']
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'

    GENDERS = (
        ('m', "Мужчина"),
        ('f', "Женщина"))

    gender = models.CharField(choices=GENDERS, max_length=1, default='')
    birth_date = models.DateField(default="2000-09-12")
    image = models.ImageField(upload_to='user/image/logo/%Y/%m/', null=True, blank=True)
    is_block = models.BooleanField(default=0)

    REQUIRED_FIELDS = []

    def get_email(self):
        return self.username

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        super(CustomUser, self).save(*args, **kwargs)
        if self.image:
            image = Image.open(self.image.path)
            image = crop_center_v2(image)
            image.save(self.image.path)


class Code(models.Model):
    email = models.EmailField(max_length=100, unique=True, primary_key=True, editable=False)
    code = models.CharField(max_length=6)
    time = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.code = ''.join(["{}".format(randint(0, 9)) for num in range(0, self._meta.get_field('code').max_length)])
        super(Code, self).save()

    def life(self):
        time_zone = timezone(settings.TIME_ZONE)
        time = datetime.datetime.now(time_zone)
        if (time - self.time).seconds < settings.CODE_LIFE_SECONDS:
            return True
        return False


class Theme(models.Model):
    theme = models.CharField(max_length=50)


class Settings(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, null=True, blank=True, on_delete=models.SET_NULL)
    online = models.PositiveIntegerField(default=0)


