from django.urls import path

from .views import (
    FeedbackViewSet,
    FeedbackAnswerCreate,
    FeedbackAnswerViewSet,
    FeedbackListView,
    FeedbackCreateView,
    FeedbackAnswerListView,
)

urlpatterns = [
    path(
        "feedbacks/<int:pk>/",
        FeedbackViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        ), name="feedback-viewset"
    ),
    path(
        "feedbacks/<int:pk>/answers/list/", FeedbackAnswerListView.as_view(),
        name="feedback-answer-list"
    ),
    path(
        "answers/create/", FeedbackAnswerCreate.as_view(),
        name="feedback-answer-create"
    ),
    path(
        "answers/<int:pk>/",
        FeedbackAnswerViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        ),
        name="feedback-answer-viewset"
    ),
    path(
        "feedbacks/list/<int:establishment_id>/", FeedbackListView.as_view(),
        name="feedback-list"
    ),
    path(
        "feedbacks/create/", FeedbackCreateView.as_view(),
        name="feedback-create"
    ),
]
