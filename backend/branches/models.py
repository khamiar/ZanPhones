from django.db import models


class Branch(models.Model):

    name = models.CharField(max_length=150)

    city = models.CharField(max_length=100)

    address = models.TextField()

    whatsapp_number = models.CharField(max_length=20)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class BranchStock(models.Model):

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="stock_items"
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="branch_stock"
    )

    quantity = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["branch", "product"],
                name="unique_product_per_branch"
            )
        ]

    def __str__(self):
        return f"{self.product.name} - {self.branch.name}"