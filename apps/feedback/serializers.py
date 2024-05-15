from .models import FeedbackAnswer, Feedback
from .serializers_services import SerializerRepresentationService
from .schema_definitions import feedback_schema, feedback_answer_schema


@feedback_answer_schema
class FeedbackAnswerSerializer(SerializerRepresentationService):

    class Meta:
        model = FeedbackAnswer
        fields = (
            "id",
            "feedback",
            "user",
            "created_at",
            "text",
        )


@feedback_schema
class FeedbackSerializer(SerializerRepresentationService):

    class Meta:
        model = Feedback
        fields = (
            "id",
            "user",
            "created_at",
            "establishment",
            "text",
        )


@feedback_schema
class FeedbackCreateUpdateSerializer(SerializerRepresentationService):

    class Meta:
        model = Feedback
        fields = (
            "id",
            "user",
            "created_at",
            "establishment",
            "text",
        )

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        feedback = Feedback.objects.create(**validated_data)
        return feedback


@feedback_answer_schema
class FeedbackAnswerCreateUpdateSerializer(SerializerRepresentationService):

    class Meta:
        model = FeedbackAnswer
        fields = (
            "id",
            "user",
            "feedback",
            "created_at",
            "text",
        )

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        feedback_answer = FeedbackAnswer.objects.create(**validated_data)
        return feedback_answer
