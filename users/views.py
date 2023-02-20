from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ViewSet, ModelViewSet

from .models import CustomUser, Code
from .permissions import IsOwner
from .serializers import *

from djoser.views import UserViewSet as DjoserUserViewSet


class UserViewSet(DjoserUserViewSet):
    def create(self, request, *args, **kwargs):
        self.check_code(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'])
    def check_code(self, request, *args, **kwargs):
        code = request.data.get('code', '')
        if not code:
            raise ValidationError('pass the "code" parameter')

        try:

            code_obj = Code.objects.get(email=request.data['email'])

            if not code_obj.life():
                raise ValidationError('code is died, trying with new code')

            if code != code_obj.code:
                raise ValidationError('code is wrong')

        except Code.DoesNotExist:
            raise ValidationError("code is undefined")

    @action(detail=False, methods=['get'])
    def check_mail(self, request):
        email = request.GET.get('email', '')
        if not email:
            raise ValidationError('pass the "email" parameter')
        exist = User.objects.filter(email=email).exists()
        return Response(exist)


class UserSimpleList(mixins.ListModelMixin,
                     GenericViewSet):
    serializer_class = UserSimpleSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.exclude(pk=self.request.user.pk)


class CodeViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = Code.objects.all()
    serializer_class = CheckMailCodeSerializer
