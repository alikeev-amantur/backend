from rest_framework.generics import (
    RetrieveAPIView,
    DestroyAPIView,
    UpdateAPIView
)
from rest_framework.viewsets import ViewSetMixin
from happyhours.permissions import (
    IsUserObjectOwner,
    IsAdmin,
    IsFeedbackAnswerOwner,
)


class FeedbackPermissions:
    def get_permissions(self):
        if self.action == "retrieve":
            permissions = []
        elif self.action in ("update", "destroy"):
            permissions = [IsUserObjectOwner]
        else:
            permissions = [IsAdmin]
        return [permission() for permission in permissions]


class FeedbackAnswerPermissions:

    def get_permissions(self):
        if self.action == "retrieve":
            permissions = []
        elif self.action in ("update", "destroy"):
            permissions = [IsFeedbackAnswerOwner]
        else:
            permissions = [IsAdmin]
        return [permission() for permission in permissions]


class FeedbackViewSetService(
    ViewSetMixin, RetrieveAPIView, UpdateAPIView, DestroyAPIView
):
    pass
