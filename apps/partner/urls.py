from django.urls import path

from .views import (
    EstablishmentListView,
    EstablishmentCreateView,
    EstablishmentViewSet,
    MenuView,
    FeedbackListView,
    FeedbackCreateView,
    FeedbackViewSet,
    FeedbackAnswerCreate,
    FeedbackAnswerViewSet,
)

urlpatterns = [
    path("establishment/list/", EstablishmentListView.as_view()),
    path("establishment/create/", EstablishmentCreateView.as_view()),
    path(
        "establishment/<int:pk>/",
        EstablishmentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
    path("menu/<int:pk>/", MenuView.as_view()),
    path("establishment/<int:pk>/feedback_list/", FeedbackListView.as_view()),
    path("establishment/<int:pk>/feedback_create/", FeedbackCreateView.as_view()),
    path(
        "establishment/feedback/<int:pk>/",
        FeedbackViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        )
    ),
    path("establishment/feedback/<int:pk>/answer_create/", FeedbackAnswerCreate.as_view()),
    path("establishment/feedback/answer/<int:pk>/", FeedbackAnswerViewSet.as_view(
        {
            "get": "retrieve",
            "put": "update",
            "delete": "destroy",
        }
    ))
]
