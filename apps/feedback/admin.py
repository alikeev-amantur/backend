from django.contrib import admin

from .models import Feedback, FeedbackAnswer


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "display_user",
        "created_at",
        "establishment",
    )

    fields = (
        "user",
        "display_user",
        "establishment",
        "text",
    )


@admin.register(FeedbackAnswer)
class FeedbackAnswerAdmin(admin.ModelAdmin):

    list_display = (
        "feedback",
        "user",
        "display_user",
        "created_at",
    )

    fields = (
        "feedback",
        "user",
        "display_user",
        "text",
    )
