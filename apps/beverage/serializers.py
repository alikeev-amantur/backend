from rest_framework import serializers
from .models import Beverage, Category
from ..partner.models import Establishment


class CategorySerializer(serializers.ModelSerializer):
    beverages = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="beverage-detail"
    )

    class Meta:
        model = Category
        fields = ["id", "name", "beverages"]


class BeverageSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")
    establishment_name = serializers.ReadOnlyField(source="establishment.name")
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True, source="category"
    )
    establishment_id = serializers.PrimaryKeyRelatedField(
        queryset=Establishment.objects.all(), write_only=True, source="establishment"
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
            "category_id",
            "establishment_name",
            "establishment_id",
        ]

    def validate_price(self, value):
        """
        Check that the price is not negative.
        """
        if value < 0:
            raise serializers.ValidationError(
                "The price must be a non-negative number."
            )
        return value
