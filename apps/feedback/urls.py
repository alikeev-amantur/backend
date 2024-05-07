from django.urls import path

from .views import (
    FeedbackListView,
    FeedbackCreateView,
    FeedbackViewSet,
    FeedbackAnswerCreate,
    FeedbackAnswerViewSet,
)

urlpatterns = [
    path(
        "<int:pk>/",
        FeedbackViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        )
    ),
    path("<int:pk>/answer_create/", FeedbackAnswerCreate.as_view()),
    path("answer/<int:pk>/", FeedbackAnswerViewSet.as_view(
        {
            "get": "retrieve",
            "put": "update",
            "delete": "destroy",
        }
    )),
]
