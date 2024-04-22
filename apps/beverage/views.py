from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404

# from .filters import BeverageFilter
from .models import Category, Beverage
from .serializers import CategorySerializer, BeverageSerializer

# from django_filters import rest_framework as filters

from ..partner.models import Establishment


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BeverageViewSet(viewsets.ModelViewSet):
    queryset = Beverage.objects.all().select_related("category", "establishment")
    serializer_class = BeverageSerializer
    # filter_backends = (filters.DjangoFilterBackend,)
    # filterset_class = BeverageFilter


class MenuViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BeverageSerializer

    def get_queryset(self):
        establishment_id = self.kwargs.get("establishment_id")
        establishment = get_object_or_404(Establishment, id=establishment_id)
        return Beverage.objects.filter(establishment=establishment).select_related(
            "category", "establishment"
        )

    def list(self, request, *args, **kwargs):
        if not self.get_queryset().exists():
            raise NotFound(
                "No beverages found for this establishment or establishment does not exist."
            )
        return super().list(request, *args, **kwargs)
