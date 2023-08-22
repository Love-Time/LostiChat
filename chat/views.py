import math

from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.http.response import FileResponse
from rest_framework import mixins
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .permissions import *
from .serializers import *



class DuoConversationViewSet(mixins.RetrieveModelMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    queryset = Conversation.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(members=self.request.user, type="duo")


class DialogMessageLastList(mixins.ListModelMixin,
                            GenericViewSet):
    queryset = Dialog.objects.all()
    serializer_class = DialogSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Dialog.objects.raw(f'''Select *, max(time), sender_id + recipient_id as my_sum from {Dialog._meta.db_table}
                                            where (sender_id == {self.request.user.id}  or recipient_id == {self.request.user.id}) 
                                            GROUP BY my_sum
                                            ORDER BY time DESC''')
        return queryset


class DialogMessagePagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = "page_size"
    max_page_size = 200


class DialogMessageViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           GenericViewSet):
    serializer_class = DialogSerializer
    queryset = Dialog.objects.all()
    permission_classes = (IsAuthenticated, IsOwner)
    pagination_class = DialogMessagePagination

    def get_queryset(self):
        return Dialog.objects.filter(Q(recipient=self.request.user) | Q(sender=self.request.user))

    def get_serializer_class(self):
        if self.action == "create":
            return DialogCreateSerializer
        return DialogSerializer


class DialogApiView(APIView, DialogMessagePagination):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        queryset = Dialog.objects.filter(Q(sender_id=self.request.user.id) & Q(recipient_id=pk) |
                                         Q(sender_id=pk) & Q(recipient_id=self.request.user.id))
        data = self.paginate_queryset(queryset, request, view=self)
        serializer = DialogSerializer(data, many=True, context={'request': request})

        return self.get_paginated_response(serializer.data)


class AttachmentsImagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        queryset = list(Image.objects.filter(Q(dialog__sender_id=self.request.user.id) & Q(dialog__recipient_id=pk) |
                                             Q(dialog__sender_id=pk) & Q(dialog__recipient_id=self.request.user.id)))
        images = ImageSerializer(queryset, many=True).data
        return Response(status=200, data=images)


class MediaAccess(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        access_granted = False

        user = request.user
        print("FFFFFFFFFFFFFFFFFFFFFFFF", user)
        if user != AnonymousUser:
            image = get_object_or_404(Image, pk=pk)
            if user.is_staff:
                access_granted = True
            else:
                if image.dialog.sender == user or image.dialog.recipient == user:
                    access_granted = True

        if access_granted:
            img = open(image.image.path, 'rb')
            response = FileResponse(img)
            return response
        else:
            return HttpResponseForbidden('Not authorized to access this media.')

# def media_access(request, pk):
#     access_granted = False
#
#     user = request.user
#     print("FFFFFFFFFFFFFFFFFFFFFFFF", user)
#     if user != AnonymousUser:
#         image = get_object_or_404(Image, pk=pk)
#         if user.is_staff:
#             access_granted = True
#         else:
#             if image.dialog.sender == user or image.dialog.recipient == user:
#                 access_granted = True
#
#
#     if access_granted:
#         #img = open(image.image.path, 'rb')
#         response = FileResponse(image.image)
#         return response
#     else:
#         return HttpResponseForbidden('Not authorized to access this media.')


# if access_granted:
#     response = HttpResponse()
#     # Content-type will be detected by nginx
#     del response['Content-Type']
#     response['X-Accel-Redirect'] = '/media/' + path
#     return response
#
# else:
#     return HttpResponseForbidden('Not authorized to access this media.')
