from rest_framework import permissions


class IsUserOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_superuser


class IsPartnerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'partner' or request.user.is_superuser


class IsPartnerOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (obj.owner == request.user or request.user.role == 'partner'
                or request.user.is_superuser)
