from rest_framework import serializers
from .models import Branch, BranchStock


class BranchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Branch
        fields = "__all__"


class BranchStockSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    branch_name = serializers.CharField(
        source="branch.name",
        read_only=True
    )

    class Meta:
        model = BranchStock
        fields = [
            "id",
            "branch",
            "branch_name",
            "product",
            "product_name",
            "quantity",
            "updated_at",
        ]