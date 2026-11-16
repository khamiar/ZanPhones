from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Branch, BranchStock
from .serializers import BranchSerializer, BranchStockSerializer


class BranchViewSet(ReadOnlyModelViewSet):

    queryset = Branch.objects.filter(is_active=True)

    serializer_class = BranchSerializer


class BranchStockViewSet(ReadOnlyModelViewSet):

    queryset = BranchStock.objects.select_related(
        "branch",
        "product"
    )

    serializer_class = BranchStockSerializer