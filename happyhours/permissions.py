from rest_framework import permissions


class IsUserOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            (obj == request.user or request.user.is_superuser or
             not request.user.is_anonymous) and not request.user.is_blocked
        )


class IsUserObjectOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            (obj.user == request.user or request.user.is_superuser)
            and not request.user.is_blocked
        )


class IsPartnerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user.is_authenticated and request.user.role
             in ('admin', 'partner') or request.user.is_superuser)
            and not request.user.is_blocked)


class IsPartnerOwner(permissions.BasePermission):
    """
    Check if user with Partner role is owner of establishment or beverage
    """
    def has_object_permission(self, request, view, obj):
        direct_owner = hasattr(obj, 'owner') and obj.owner == request.user

        establishment_owner = hasattr(obj, 'establishment') and \
                              hasattr(obj.establishment, 'owner') and \
                              obj.establishment.owner == request.user

        return bool(
            (direct_owner or establishment_owner or request.user.is_superuser)
            and not request.user.is_blocked
        )


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user.is_authenticated and request.user.role == 'admin' or
             request.user.is_superuser) and not request.user.is_blocked
        )


class IsPartnerAndAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user.is_authenticated and request.user.role
             in ('admin', 'partner') or request.user.is_superuser)
            and not request.user.is_blocked
        )


class IsNotAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(not request.user.is_authenticated)


class IsAuthenticatedAndNotAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user and request.user.is_authenticated and
             request.user.role != 'admin' and not request.user.is_superuser)
            and not request.user.is_blocked
        )


class IsClientOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user.role == "client" or request.user.is_superuser and
             request.user.is_authenticated) and not request.user.is_blocked
        )


class IsAuthenticatedAndNotBlocked(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and not request.user.is_blocked)


class IsFeedbackAnswerOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            (obj.user == request.user or request.user.is_superuser or
             obj.feedback.establishment.owner == request.user)
            and not request.user.is_blocked
        )
