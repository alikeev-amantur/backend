from rest_framework import serializers

from .models import Establishment, QRCode
from .utils import phone_number_validation
from ..beverage.serializers import BeverageSerializer


class QRCodeSerializer(serializers.ModelSerializer):
    qr_code_image = serializers.SerializerMethodField()

    class Meta:
        model = QRCode
        fields = [
            "id",
            "qr_code_image",
        ]

    def get_qr_code_image(self, obj):
        request = self.context.get("request")
        if obj.qr_code_image and request:
            return request.build_absolute_uri(obj.qr_code_image.url)
        return None


class EstablishmentSerializer(serializers.ModelSerializer):
    """
    Main serializer for Establishment model
    """

    qr_code = QRCodeSerializer(read_only=True)

    class Meta:
        model = Establishment
        fields = (
            "id",
            "name",
            "location",
            "description",
            "phone_number",
            "logo",
            "address",
            "owner",
            "qr_code",
        )

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.logo != "":
            return request.build_absolute_uri(obj.logo.url)
        return ""

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["logo"] = self.get_image_url(instance)
        representation["owner"] = instance.owner.username
        return representation


class EstablishmentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Establishment
        fields = (
            "id",
            "name",
            "location",
            "description",
            "phone_number",
            "logo",
            "address",
            "owner",
        )

    def create(self, validated_data):
        """
        Create and return a new `Establishment` instance.
        :param validated_data:
        :return:
        """
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


class MenuSerializer(serializers.ModelSerializer):
    beverages = BeverageSerializer(many=True, read_only=True)

    class Meta:
        model = Establishment
        fields = [
            "id",
            "name",
            "location",
            "description",
            "phone_number",
            "address",
            "logo",
            "beverages",
        ]
