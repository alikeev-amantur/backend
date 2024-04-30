from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from .models import Beverage, Category
from .schema_definitions import beverage_serializer_schema
from ..partner.models import Establishment


class CategorySerializer(serializers.ModelSerializer):
    beverages = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="v1:beverage-detail"
    )

    class Meta:
        model = Category
        fields = ["id", "name", "beverages"]


@beverage_serializer_schema
class BeverageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )
    establishment_name = serializers.CharField(
        source="establishment.name",
        read_only=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source="category",
        help_text="ID of the category to which this beverage belongs."
    )
    establishment_id = serializers.PrimaryKeyRelatedField(
        queryset=Establishment.objects.all(),
        write_only=True,
        source="establishment",
        help_text="ID of the establishment that offers this beverage."
    )

    class Meta:
        model = Beverage
        fields = [
            "id",
            "name",
            "price",
            "description",
            "availability_status",
            "category_name",
            "establishment_name",
            "category_id",
            "establishment_id",
        ]

    def validate_establishment_id(self, value):
        user = self.context['request'].user
        if value.owner != user:
            raise serializers.ValidationError("User does not own this establishment.")
        return value

    def validate_price(self, value):
        """
        Check that the price is not negative.
        """
        if value < 0:
            raise serializers.ValidationError(
                "The price must be a non-negative number."
            )
        return value
