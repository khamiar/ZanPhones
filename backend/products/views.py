from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer


class ProductViewSet(ReadOnlyModelViewSet):

    queryset = Product.objects.filter(
        is_active=True
    ).select_related("category").prefetch_related("images")

    serializer_class = ProductSerializer


class CategoryViewSet(ReadOnlyModelViewSet):

    queryset = Category.objects.all()

    serializer_class = CategorySerializer