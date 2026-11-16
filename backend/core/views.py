from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import CurrencyConfig
from .serializers import CurrencyConfigSerializer


class CurrencyConfigViewSet(ReadOnlyModelViewSet):

    queryset = CurrencyConfig.objects.all()

    serializer_class = CurrencyConfigSerializer