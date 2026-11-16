from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Customer(models.Model):

    full_name = models.CharField(max_length=150)

    phone_number = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

class Order(models.Model):

    class Currency(models.TextChoices):
        TZS = "TZS", "Tanzanian Shilling"
        USD = "USD", "US Dollar"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    order_number = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="orders"
    )

    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.PROTECT,
        related_name="orders"
    )

    managed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.TZS
    )

    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.order_number)

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="order_items"
    )

    product_name = models.CharField(max_length=200)

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    def __str__(self):
        return self.product_name

