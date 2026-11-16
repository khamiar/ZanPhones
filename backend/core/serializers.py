from rest_framework import serializers
from .models import CurrencyConfig


class CurrencyConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = CurrencyConfig
        fields = "__all__"