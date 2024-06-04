from drf_spectacular.utils import extend_schema
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
)

from happyhours.permissions import (
    IsPartnerUser,
    IsClientOnly,
    IsAuthenticatedAndNotBlocked,
)

from .models import Feedback, FeedbackAnswer
from .serializers import (
    FeedbackSerializer,
    FeedbackAnswerSerializer,
    FeedbackCreateUpdateSerializer,
    FeedbackAnswerCreateUpdateSerializer,
)
from .views_services import (
    FeedbackViewSetService,
    FeedbackPermissions,
    FeedbackAnswerPermissions
)


@extend_schema(tags=["Feedbacks"])
class FeedbackListView(ListAPIView):
    """
    Feedback's list view

    ### Fields:
    - `user`: Owner of the feedback
    - `created_at`: Time of creation
    - `establishment`: Establishment of the feedback
    - `text`: Content of the feedback

    ### Access Control:
    - Everyone

    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        establishment = self.request.resolver_match.kwargs["establishment_id"]
        if establishment:
            queryset = Feedback.objects.filter(establishment=establishment)
            return queryset
        return Feedback.objects.none()


@extend_schema(tags=["Feedbacks"])
class FeedbackAnswerListView(ListAPIView):
    """
    Feedback's Answers list view

    ### Fields:
    - `feedback`: ID of the feedback
    - `user`: Owner of the feedback's answer
    - `created_at`: Time of creation
    - `text`: Content of the feedback's answer

    ### Access Control:
    - Everyone

    """
    queryset = FeedbackAnswer.objects.all()
    serializer_class = FeedbackAnswerSerializer

    def get_queryset(self):
        queryset = FeedbackAnswer.objects.all()
        feedback = self.request.resolver_match.kwargs["pk"]
        if feedback > 0:
            queryset = FeedbackAnswer.objects.filter(feedback=feedback)
        return queryset


@extend_schema(tags=["Feedbacks"])
class FeedbackCreateView(CreateAPIView):
    """
    Feedback's creation view

    ### Fields:
    - `user`: Owner of the feedback
    - `created_at`: Time of creation
    - `establishment`: Establishment of the feedback
    - `text`: Content of the feedback

    ### Access Control:
    - Only Client user

    """

    queryset = Feedback.objects.all()
    serializer_class = FeedbackCreateUpdateSerializer
    permission_classes = [IsClientOnly]


@extend_schema(tags=["Feedbacks"])
class FeedbackViewSet(
    FeedbackPermissions,
    FeedbackViewSetService
):
    """
    Feedback's CRUD

    ### Fields:
    - `user`: Owner of the feedback
    - `created_at`: Time of creation
    - `establishment`: Establishment of the feedback
    - `text`: Content of the feedback

    ### Access Control:
    - Retrieve - anonymous user
    - Updating or deleting - Owner of feedback or admin and superuser

    """

    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer


@extend_schema(tags=["Feedbacks"])
class FeedbackAnswerCreate(CreateAPIView):
    """
    Feedback's answers' creation view

    ### Fields:
    - `feedback`: Feedback of the answer
    - `user`: Owner of the answer
    - `created_at`: Time of creation
    - `text`: Content of the feedback

    ### Access Control:
    - Admin or superuser

    """

    queryset = FeedbackAnswer.objects.all()
    serializer_class = FeedbackAnswerCreateUpdateSerializer
    permission_classes = [IsAuthenticatedAndNotBlocked]


@extend_schema(tags=["Feedbacks"])
class FeedbackAnswerViewSet(
    FeedbackAnswerPermissions,
    FeedbackViewSetService
):
    """
    Feedback's answers' CRUD

    ### Fields:
    - `feedback`: Feedback of the answer
    - `user`: Owner of the answer
    - `created_at`: Time of creation
    - `text`: Content of the feedback

    ### Access Control:
    - Retrieve - anonymous user
    - Updating or deleting - Owner of feedback or admin and superuser

    """

    queryset = FeedbackAnswer.objects.all()
    serializer_class = FeedbackAnswerSerializer
