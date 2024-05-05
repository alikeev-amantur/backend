from drf_spectacular.utils import (
    extend_schema_field,
)
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Establishment
from .schema_definitions import establishment_serializer_schema, menu_serializer_schema
from .utils import phone_number_validation
from ..beverage.serializers import BeverageSerializer


# class QRCodeSerializer(serializers.ModelSerializer):
#     qr_code_image = serializers.SerializerMethodField()
#
#     class Meta:
#         model = QRCode
#         fields = [
#             "id",
#             "qr_code_image",
#         ]
#
#     @extend_schema_field(serializers.URLField())
#     def get_qr_code_image(self, obj):
#         request = self.context.get("request")
#         if obj.qr_code_image and request:
#             return request.build_absolute_uri(obj.qr_code_image.url)
#         return None



# @establishment_serializer_schema
class EstablishmentSerializer(GeoFeatureModelSerializer):
    """
    Main serializer for Establishment model
    """

    # qr_code = QRCodeSerializer(read_only=True)

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
            # "qr_code",
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
    # qr_code = QRCodeSerializer(read_only=True)

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
            # "qr_code",
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

# @menu_serializer_schema
# class MenuSerializer(serializers.ModelSerializer):
#     beverages = BeverageSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = Establishment
#         fields = [
#             "id",
#             "name",
#             "location",
#             "description",
#             "phone_number",
#             "address",
#             "logo",
#             "happyhours_start",
#             "happyhours_end",
#             "beverages",
#         ]
