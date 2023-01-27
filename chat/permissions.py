from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions

class IsOwnerOrReadonly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.sender == request.user:
            return True
        return False