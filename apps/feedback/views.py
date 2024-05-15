from drf_spectacular.utils import extend_schema
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
)
from rest_framework.permissions import IsAuthenticated

from happyhours.permissions import IsAdmin

from .models import Feedback, FeedbackAnswer
from .serializers import (
    FeedbackSerializer,
    FeedbackAnswerSerializer,
    FeedbackCreateUpdateSerializer,
    FeedbackAnswerCreateUpdateSerializer,
)
from .views_services import FeedbackViewSetService


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
        if feedback:
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
    - Authenticated user

    """

    queryset = Feedback.objects.all()
    serializer_class = FeedbackCreateUpdateSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(tags=["Feedbacks"])
class FeedbackViewSet(FeedbackViewSetService):
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
    permission_classes = [IsAdmin]


@extend_schema(tags=["Feedbacks"])
class FeedbackAnswerViewSet(FeedbackViewSetService):
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
