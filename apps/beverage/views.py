from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from .models import Category, Beverage
from .serializers import CategorySerializer, BeverageSerializer


@extend_schema(tags=["Beverages"])
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@extend_schema(tags=["Beverages"])
class BeverageViewSet(viewsets.ModelViewSet):
    queryset = Beverage.objects.all().select_related("category", "establishment")
    serializer_class = BeverageSerializer
