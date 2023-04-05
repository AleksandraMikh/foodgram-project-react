from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        print(request.method, permissions.SAFE_METHODS)
        if not request.user.is_authenticated or request.user != obj.author:
            print(request.method, permissions.SAFE_METHODS)
            return request.method in permissions.SAFE_METHODS
        # if request.user.is_authenticated:
        #     if request.user == obj.author:
        return True


class NotPut(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'PUT':
            return False
        return True
