from rest_framework import permissions


class IsUserOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(obj == request.user or request.user.role == 'admin')


class IsPartnerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and request.user.role in
            ('admin', 'partner')
        )


class IsPartnerOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            (obj.owner == request.user and request.user.role == 'partner')
            or (request.user.role == 'admin')
        )


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and request.user.role in
            ('admin', 'staff')
        )


class IsPartnerStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and request.user.role in
            ('admin', 'staff', 'partner')
        )


class IsNotAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(not request.user.is_authenticated)


class IsBlockedUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_blocked)
