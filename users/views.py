from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from config.settings import EMAIL_ACTIVATION
from .serializers import *


class UserViewSet(DjoserUserViewSet):
    def get_permissions(self):
        if self.action == "check_mail" or self.action == "check_code":
            return [AllowAny()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        self.check_code(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'])
    def check_code(self, request, *args, **kwargs):
        if not EMAIL_ACTIVATION:
            return Response(status=status.HTTP_204_NO_CONTENT)
        code = request.GET.get('code', request.data.get('code', ''))
        email = request.GET.get('email', request.data.get('email', ''))

        if not code:
            return Response({'type': 0, 'message': 'pass the "code" parameter'}, status=status.HTTP_403_FORBIDDEN)
        if not email:
            return Response({'type': 1, 'message': 'pass the "email" parameter'}, status=status.HTTP_403_FORBIDDEN)
        try:

            code_obj = Code.objects.get(email=email)

            if not code_obj.life():
                return Response({'type': 2, 'message': 'code is died, trying with new code'},
                                status=status.HTTP_403_FORBIDDEN)

            if code != code_obj.code:
                return Response({'type': 3, 'message': 'code is wrong'}, status=status.HTTP_403_FORBIDDEN)
        except Code.DoesNotExist:
            return Response({'type': 4, 'message': 'code is undefined'}, status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def check_mail(self, request):
        email = request.GET.get('email', '')
        if not email:
            raise ValidationError('pass the "email" parameter')
        exist = User.objects.filter(email=email).exists()
        return Response(exist)


class UserSimpleList(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                     GenericViewSet):
    serializer_class = UserSimpleSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        return User.objects.exclude(pk=self.request.user.pk)


class CodeViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = Code.objects.all()
    serializer_class = CheckMailCodeSerializer


class SettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return Settings.objects.get(pk=pk)

    def patch(self, request):
        obj = self.get_object(request.user.id)
        serializer = SettingsSerializer(obj, data=request.data,
                                        partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=201, data=serializer.data)
        return Response(status=400)




