from rest_framework import serializers

from .models import Establishment


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
