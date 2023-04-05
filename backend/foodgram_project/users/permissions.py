from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or request.user != obj.author:
            return request.method in permissions.SAFE_METHODS
        # if request.user.is_authenticated:
        #     if request.user == obj.author:
        return True
