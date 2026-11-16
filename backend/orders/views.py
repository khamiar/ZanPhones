from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(ReadOnlyModelViewSet):

    permission_classes = [IsAdminUser]

    queryset = Order.objects.select_related(
        "customer",
        "branch"
    ).prefetch_related("items")

    serializer_class = OrderSerializer