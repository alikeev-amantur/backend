from rest_framework import permissions


class IsUserOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(obj == request.user or request.user.is_superuser)


class IsPartnerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and request.user.role in
            ('admin', 'partner') or request.user.is_superuser
        )


class IsPartnerOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            (obj.owner == request.user and request.user.role == 'partner')
            or (request.user.role == 'admin') or request.user.is_superuser
        )


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and request.user.role == 'admin'
            or request.user.is_superuser
        )


class IsPartnerAndAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and request.user.role in
            ('admin', 'partner') or request.user.is_superuser
        )


class IsNotAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(not request.user.is_authenticated)
