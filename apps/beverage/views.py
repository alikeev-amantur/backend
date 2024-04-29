from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions

from happyhours.permissions import IsPartnerOwner, IsAdmin, IsPartnerUser
from .models import Category, Beverage
from .serializers import CategorySerializer, BeverageSerializer


@extend_schema(tags=["Categories"])
class CategoryViewSet(viewsets.ModelViewSet):
    """
    Provides a set of CRUD operations for categories.

    Each category includes a hyperlink to the associated beverages

    ## Endpoints and Permissions
    - **List (GET /categories/)**: Retrieve all categories. Requires authentication.
    - **Retrieve (GET /categories/{id}/)**: Retrieve a specific category by its ID.
    Requires authentication.
    - **Create (POST /categories/)**: Create a new category.
     Requires user role admin
    - **Update (PUT/PATCH /categories/{id}/)**: Update an existing category  .
     Requires user role admin
    - **Delete (DELETE /categories/{id}/)**: Delete a category.
     Requires admin privileges.

    ## Related Fields
    - `beverages`: A list of URLs pointing to detailed views of beverages that belong to a category.
     This field is read-only.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):

        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


@extend_schema(tags=["Beverages"])
class BeverageViewSet(viewsets.ModelViewSet):
    """
    Beverage ViewSet that handles creating, retrieving, updating, and deleting beverage items.

    ### Fields:
    - `price`: The price of the beverage. Must be a non-negative number.
    - `category_name`: The name of the category to which the beverage belongs (read-only).
    - `establishment_name` : The name of the establishment to which the beverage belongs (read-only).
    - `category_id`: The ID of the category to which the beverage should be linked (write-only).
    - `establishment_id`: The ID of the establishment where the beverage is served (write-only).

    ### Validation:
    - The `price` field must be a non-negative number.
    """

    queryset = Beverage.objects.all().select_related("category", "establishment")
    serializer_class = BeverageSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == "create":
            permission_classes = [IsPartnerUser]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsPartnerOwner]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
