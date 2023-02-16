from rest_framework import permissions


class IsOwner(permissions.IsAuthenticated, permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.first_user == request.user:
            return True
        return False


class IsFriend(permissions.IsAuthenticated, permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.second_user == request.user:
            return True
        return False
