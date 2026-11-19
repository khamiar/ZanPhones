from unittest.mock import call

from django.db import transaction
from rest_framework import serializers
from decimal import Decimal

from branches.models import Branch, BranchStock
from .models import Customer, Order, OrderItem
from .utils import generate_whatsapp_link

class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"

class OrderItemInputSerializer(serializers.Serializer):

    product_id = serializers.IntegerField()

    quantity = serializers.IntegerField(
        min_value=1
    )

class OrderCreateSerializer(serializers.Serializer):

    customer = serializers.DictField()

    branch_id = serializers.IntegerField()

    currency = serializers.ChoiceField(
        choices=["TZS", "USD"]
    )

    items = OrderItemInputSerializer(
        many=True
    )

    
    def validate_customer(self, value):
        name = value.get("name")
        phone = value.get("phone")

        if not isinstance(name, str) or not isinstance(phone, str):
            raise serializers.ValidationError(
                "Customer name and phone must be text."
            )

        name = name.strip()
        phone = phone.strip()

        if not name or not phone:
            raise serializers.ValidationError(
                "Customer name and phone are required."
            )

        if len(name) < 2:
            raise serializers.ValidationError(
                "Customer name is too short."
            )

        return {
            "name": name,
            "phone": phone
        }


    def validate_items(self, value):

        if not value:
            raise serializers.ValidationError(
                "An order must contain at least one item."
            )

        product_ids = [
            item["product_id"]
            for item in value
        ]

        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError(
                "Do not submit the same product more than once."
            )

        return value

    def validate_branch_id(self, value):

        if not Branch.objects.filter(
            id=value,
            is_active=True
        ).exists():

            raise serializers.ValidationError(
                "Selected branch is not available."
            )

        return value
    @transaction.atomic
    def create(self, validated_data):

        customer_data = validated_data["customer"]
        branch_id = validated_data["branch_id"]
        currency = validated_data["currency"]
        items_data = validated_data["items"]

        branch = Branch.objects.get(
            id=branch_id,
            is_active=True
        )

        # Lock the relevant stock records.
        product_ids = sorted(
            item["product_id"]
            for item in items_data
        )

        stock_records = list(
            BranchStock.objects
            .select_for_update()
            .filter(
                branch=branch,
                product_id__in=product_ids
            )
            .select_related("product")
            .order_by("product_id")
        )

        stock_by_product = {
            stock.product_id: stock
            for stock in stock_records
        }

        # Validate all products and quantities first.
        prepared_items = []
        total_amount = Decimal("0.00")

        for item in items_data:

            product_id = item["product_id"]
            quantity = item["quantity"]

            stock = stock_by_product.get(product_id)

            if stock is None:
                raise serializers.ValidationError({
                    "items": (
                        f"Product {product_id} is not available "
                        "at the selected branch."
                    )
                })

            product = stock.product

            if not product.is_active:
                raise serializers.ValidationError({
                    "items": (
                        f"{product.name} is not available."
                    )
                })

            if stock.quantity < quantity:
                raise serializers.ValidationError({
                    "items": (
                        f"Not enough stock for {product.name}. "
                        f"Available: {stock.quantity}."
                    )
                })

            if currency == "TZS":
                unit_price = product.price_tzs
            else:
                unit_price = product.price_usd

            if unit_price is None or unit_price < Decimal("0.00"):
                raise serializers.ValidationError({
                    "items": f"Invalid price for {product.name}."
                })

            subtotal = unit_price * quantity

            total_amount += subtotal

            prepared_items.append({
                "product": product,
                "product_name": product.name,
                "unit_price": unit_price,
                "quantity": quantity,
                "subtotal": subtotal,
                "stock": stock
            })


        # Create or retrieve the customer.
        customer, created = Customer.objects.get_or_create(
            phone_number=customer_data["phone"],
            defaults={
                "full_name": customer_data["name"]
            }
        )

        if not created:
            customer.full_name = customer_data["name"]
            customer.save(update_fields=["full_name"])

        
        # Create the order.
        order = Order.objects.create(
            customer=customer,
            branch=branch,
            currency=currency,
            total_amount=total_amount,
            status="PENDING"
        )

        # Save order items and deduct stock.
        for item in prepared_items:

            OrderItem.objects.create(
                order=order,
                product=item["product"],
                product_name=item["product_name"],
                unit_price=item["unit_price"],
                quantity=item["quantity"],
                subtotal=item["subtotal"]
            )

            item["stock"].quantity -= item["quantity"]

            item["stock"].save(
                update_fields=["quantity"]
            )

        return order

    


class OrderResponseSerializer(serializers.ModelSerializer):

    branch_name = serializers.CharField(
        source="branch.name",
        read_only=True
    )

    whatsapp_number = serializers.CharField(
        source="branch.whatsapp_number",
        read_only=True
    )


    customer_name = serializers.CharField(
        source="customer.full_name",
        read_only=True
    )

    customer_phone = serializers.CharField(
        source="customer.phone_number",
        read_only=True
    )

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    whatsapp_link = serializers.SerializerMethodField()

    def get_whatsapp_link(self, obj):
        return generate_whatsapp_link(obj)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "branch_name",
            "whatsapp_number",
            "whatsapp_link",
            "customer_name",
            "customer_phone",
            "items",
            "currency",
            "total_amount",
            "status",
            "created_at"
        ]


    