from drf_spectacular.utils import extend_schema
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSetMixin

from .models import Feedback, FeedbackAnswer
from .serializers import (
    FeedbackSerializer,
    FeedbackCreateUpdateSerializer,
    FeedbackAnswerCreateUpdateSerializer,
    FeedbackAnswerSerializer
)
from happyhours.permissions import (
    IsUserObjectOwner,
    IsAdmin,
)


@extend_schema(tags=["Feedbacks"])
class FeedbackListView(ListAPIView):
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        establishment = self.request.resolver_match.kwargs['pk']
        return Feedback.objects.filter(establishment=establishment)


@extend_schema(tags=["Feedbacks"])
class FeedbackCreateView(CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackCreateUpdateSerializer
    permission_classes = [IsAuthenticated]


class FeedbackPermissions:
    def get_permissions(self):
        if self.action == "retrieve":
            permissions = [IsAuthenticated]
        elif self.action in ("update", "partial_update", "destroy"):
            permissions = [IsUserObjectOwner]
        else:
            permissions = [IsAdmin]
        return [permission() for permission in permissions]


@extend_schema(tags=["Feedbacks"])
class FeedbackViewSet(
    FeedbackPermissions, ViewSetMixin, RetrieveAPIView, UpdateAPIView,
    DestroyAPIView
):
    queryset = Feedback.objects.all()

    def get_serializer_class(self):
        if self.action == "update":
            return FeedbackAnswerCreateUpdateSerializer
        return FeedbackSerializer


@extend_schema(tags=["Feedbacks"])
class FeedbackAnswerCreate(CreateAPIView):
    queryset = FeedbackAnswer.objects.all()
    serializer_class = FeedbackAnswerCreateUpdateSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(tags=["Feedbacks"])
class FeedbackAnswerViewSet(
    FeedbackPermissions, ViewSetMixin, RetrieveAPIView, UpdateAPIView,
    DestroyAPIView
):
    queryset = FeedbackAnswer.objects.all()

    def get_serializer_class(self):
        if self.action == "update":
            return FeedbackAnswerCreateUpdateSerializer
        return FeedbackAnswerSerializer
