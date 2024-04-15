from rest_framework import serializers

from .models import Establishment
from .utils import phone_number_validation


class EstablishmentSerializer(serializers.ModelSerializer):
    """
    Main serializer for Establishment model
    """
    class Meta:
        model = Establishment
        fields = (
            'id',
            'name',
            'location',
            'description',
            'phone_number',
        )


class EstablishmentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Establishment
        fields = (
            'id',
            'name',
            'location',
            'description',
            'phone_number',
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
        Validating phone number. Modifying location field
        :param instance:
        :param validated_data:
        :return:
        """
        phone_number_validation(validated_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
