from rest_framework import serializers

from .models import FeedbackAnswer, Feedback
from .serializers_services import SerializerRepresentationService
from .schema_definitions import feedback_schema, feedback_answer_schema


@feedback_answer_schema
class FeedbackAnswerSerializer(SerializerRepresentationService):
    feedback = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = FeedbackAnswer
        fields = (
            "id",
            "feedback",
            "user",
            "display_user",
            "user_role",
            "created_at",
            "text",
        )


@feedback_schema
class FeedbackSerializer(SerializerRepresentationService):
    establishment = serializers.PrimaryKeyRelatedField(read_only=True)
    answers = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Feedback
        fields = (
            "id",
            "user",
            "display_user",
            "user_role",
            "created_at",
            "establishment",
            "text",
            "answers",
        )

    def get_answers(self, obj) -> bool:
        answers = FeedbackAnswer.objects.filter(feedback=obj).count()
        return answers


@feedback_schema
class FeedbackCreateUpdateSerializer(SerializerRepresentationService):

    class Meta:
        model = Feedback
        fields = (
            "id",
            "user",
            "display_user",
            "user_role",
            "created_at",
            "establishment",
            "text",
        )

    def create(self, validated_data):
        user = self.context["request"].user
        if user.role != "client":
            raise serializers.ValidationError("Only for clients")
        validated_data["user"] = user
        validated_data["display_user"] = user.name
        feedback = Feedback.objects.create(**validated_data)
        return feedback


@feedback_answer_schema
class FeedbackAnswerCreateUpdateSerializer(SerializerRepresentationService):

    class Meta:
        model = FeedbackAnswer
        fields = (
            "id",
            "user",
            "display_user",
            "feedback",
            "created_at",
            "text",
        )

    def create(self, validated_data):
        user = self.context["request"].user
        feedback = validated_data.get("feedback")

        if user.role == "admin":
            validated_data["display_user"] = "Admin"

        elif user.role == "client" and feedback.user == user:
            validated_data["display_user"] = user.name

        elif user.role == "partner" and feedback.establishment.owner == user:
            validated_data["display_user"] = feedback.establishment.name

        else:
            raise serializers.ValidationError(
                "You cannot create a feedback answer for this establishment.")

        validated_data["user"] = user
        feedback_answer = FeedbackAnswer.objects.create(**validated_data)
        return feedback_answer
