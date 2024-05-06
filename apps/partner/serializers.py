from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Establishment, Feedback, FeedbackAnswer
from .utils import phone_number_validation


# @establishment_serializer_schema
class EstablishmentSerializer(GeoFeatureModelSerializer):
    """
    Main serializer for Establishment model
    """

    class Meta:
        model = Establishment
        geo_field = "location"
        fields = (
            "id",
            "name",
            "location",
            "description",
            "phone_number",
            "logo",
            "address",
            "happyhours_start",
            "happyhours_end",
            "owner",
        )

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.logo != "":
            return request.build_absolute_uri(obj.logo.url)
        return ""

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["logo"] = self.get_image_url(instance)
        representation["owner"] = instance.owner.email
        return representation


# @establishment_serializer_schema
class EstablishmentCreateUpdateSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Establishment
        geo_field = "location"
        fields = (
            "id",
            "name",
            "location",
            "description",
            "phone_number",
            "logo",
            "address",
            "happyhours_start",
            "happyhours_end",
            "owner",
        )

    def validate_owner(self, value):
        """
        Validate that the owner is the authenticated user.
        """
        user = self.context['request'].user
        if value != user:
            raise serializers.ValidationError("You are not allowed to set the owner to another user.")
        return value

    def create(self, validated_data):
        """
        Create and return a new `Establishment` instance.
        """
        user = self.context['request'].user
        validated_data['owner'] = user
        phone_number_validation(validated_data)
        establishment = Establishment.objects.create(**validated_data)
        return establishment

    def update(self, instance, validated_data):
        """
        Update existing Establishment instance.
        :param instance:
        :param validated_data:
        :return:
        """
        phone_number_validation(validated_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class FeedbackAnswerSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = FeedbackAnswer
        fields = (
            "id",
            "feedback",
            "user",
            "created_at",
            "text",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = instance.user.email
        return representation


class FeedbackSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    feedback_answers = FeedbackAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Feedback
        fields = (
            "id",
            "user",
            "created_at",
            "establishment",
            "text",
            "feedback_answers",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = instance.user.email
        representation["establishment"] = instance.establishment.name
        return representation


class FeedbackCreateUpdateSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Feedback
        fields = (
            "id",
            "created_at",
            "text",
        )

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        establishment = self.context.get("request").resolver_match.kwargs["pk"]
        validated_data["establishment"] = Establishment.objects.get(pk=establishment)
        feedback = Feedback.objects.create(**validated_data)
        return feedback


class FeedbackAnswerCreateUpdateSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = FeedbackAnswer
        fields = (
            "id",
            "created_at",
            "text",
        )

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        feedback = self.context.get("request").resolver_match.kwargs["pk"]
        validated_data["feedback"] = Feedback.objects.get(pk=feedback)
        feedback_answer = FeedbackAnswer.objects.create(**validated_data)
        return feedback_answer
