from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import IntegrityError, transaction
from djoser.compat import get_user_email_field_name, get_user_email
from djoser.conf import settings
from rest_framework import serializers

from users.models import CustomUser, Code, Settings

User = get_user_model()


class SettingsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    online = serializers.IntegerField(read_only=True)
    class Meta:
        model = Settings
        exclude = ['id']


class UserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    settings = serializers.SerializerMethodField()

    def get_settings(self, obj):
        settings = Settings.objects.get(user=obj)
        return SettingsSerializer(settings).data

    def get_image(self, obj):
        if obj.image:
            return obj.image.url

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.USER_ID_FIELD,
            settings.LOGIN_FIELD,
            'first_name',
            'last_name',
            'gender',
            'birth_date',
            'is_block',
            'is_staff',
            'image',
            'settings',
        )
        read_only_fields = (settings.LOGIN_FIELD, 'is_block', 'is_staff')

    def update(self, instance, validated_data):
        email_field = get_user_email_field_name(User)
        if settings.SEND_ACTIVATION_EMAIL and email_field in validated_data:
            instance_email = get_user_email(instance)
            if instance_email != validated_data[email_field]:
                instance.is_active = False
                instance.save(update_fields=["is_active"])
        return super().update(instance, validated_data)


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    code = serializers.CharField(read_only=True)
    image = serializers.SerializerMethodField()
    img = serializers.ImageField(source='image', write_only=True)

    def get_image(self, obj):
        if obj.image:
            return obj.image.url

    default_error_messages = {
        "cannot_create_user": settings.CONSTANTS.messages.CANNOT_CREATE_USER_ERROR
    }

    class Meta:
        model = User
        fields = tuple(CustomUser.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
            "password", 'first_name', 'last_name', 'gender', 'birth_date', 'code', 'image', 'img',
        )

    def validate(self, attrs):
        user = CustomUser(**attrs)
        password = attrs.get("password")

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error["non_field_errors"]}
            )

        return attrs

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")

        return user

    def perform_create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            if settings.SEND_ACTIVATION_EMAIL:
                user.is_active = False
                user.save(update_fields=["is_active"])
        return user


class TokenSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source="key")
    user = UserSerializer()

    class Meta:
        model = settings.TOKEN_MODEL
        fields = ['auth_token', 'user']


class UserSimpleSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    online = serializers.SerializerMethodField()

    def get_online(self, obj):
        online = Settings.objects.get(user=obj).online
        if online > 0:
            return True
        else:
            return False

    def get_image(self, obj):
        if obj.image:
            return obj.image.url

    class Meta:
        model = User
        fields = ['pk', 'first_name', 'last_name', 'image', 'online']


class CheckMailCodeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Code
        fields = ['email']
        extra_kwargs = {
            'code': {'write_only': True},
        }
