from rest_framework import viewsets

from .filters import BeverageFilter
from .models import Category, Beverage
from .serializers import CategorySerializer, BeverageSerializer
from django_filters import rest_framework as filters


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BeverageViewSet(viewsets.ModelViewSet):
    queryset = Beverage.objects.all().select_related("category", "establishment")
    serializer_class = BeverageSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = BeverageFilter


class MenuViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BeverageSerializer

    def get_queryset(self):
        establishment_id = self.kwargs["establishment_id"]
        return Beverage.objects.filter(establishment_id=establishment_id)
