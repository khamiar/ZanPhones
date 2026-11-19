from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from .models import Product
from .serializers import ProductSerializer

from accounts.permissions import IsAdminOrManager


class ProductViewSet(ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):

        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        return [IsAdminOrManager()]

    def get_queryset(self):

        queryset = Product.objects.filter(
            is_active=True
        )

        category_id = self.request.query_params.get(
            "category"
        )

        search = self.request.query_params.get(
            "search"
        )

        if category_id:
            queryset = queryset.filter(
                category_id=category_id
            )

        if search:
            queryset = queryset.filter(
                name__icontains=search
            )

        return queryset