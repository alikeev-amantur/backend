from rest_framework import serializers
from .models import Beverage, Category
from ..partner.models import Establishment


class CategorySerializer(serializers.ModelSerializer):
    beverages = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="v1:beverage-detail"
    )

    class Meta:
        model = Category
        fields = ["id", "name", "beverages"]


class BeverageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
        allow_null=True  # Ensure the serializer allows null values for category name
    )
    establishment_name = serializers.CharField(
        source="establishment.name",
        read_only=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source="category",
        allow_null=True,  # Allow null values for category ID
        help_text="ID of the category to which this beverage belongs. Can be null if the beverage is uncategorized."
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
        swagger_schema_fields = {
            "examples": {
                "id": 1,
                "name": "Cola",
                "price": 2.50,
                "description": "Refreshing carbonated soft drink.",
                "availability_status": "Available",
                "category_name": "Soft Drinks",
                "establishment_name": "Joe's Bar",
                "category_id": 3,
                "establishment_id": 5
            }
        }

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
