from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, BeverageViewSet, MenuViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"beverages", BeverageViewSet)
router.register(
    r"beverages/by_establishment/(?P<establishment_id>[^/.]+)",
    MenuViewSet,
    basename="establishment-beverages",
)
urlpatterns = [
    path("", include(router.urls)),
]
