from rest_framework import viewsets, filters
from .models import Category, Beverage
from .serializers import CategorySerializer, BeverageSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BeverageViewSet(viewsets.ModelViewSet):
    queryset = Beverage.objects.all().select_related('category')
    serializer_class = BeverageSerializer

