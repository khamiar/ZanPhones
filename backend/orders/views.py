
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Order
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderResponseSerializer,
)
from accounts.permissions import IsBranchOrderMember


class OrderPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsBranchOrderMember]
    pagination_class = OrderPagination

    def get_queryset(self):
        user = self.request.user

        queryset = (
            Order.objects
            .select_related(
                "customer",
                "branch",
                "managed_by"
            )
            .prefetch_related("items")
            .order_by("-created_at")
        )

        if not (
            user.is_superuser
            or user.role in ["SUPER_ADMIN", "ADMIN"]
        ):
            queryset = queryset.filter(
                branch_id=user.branch_id
            )

        status_value = self.request.query_params.get("status")

        if status_value:
            if status_value not in Order.Status.values:
                raise ValidationError({
                    "status": "Invalid order status."
                })

            queryset = queryset.filter(status=status_value)

        return queryset


class OrderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsBranchOrderMember]

    def get_queryset(self):
        user = self.request.user

        queryset = (
            Order.objects
            .select_related(
                "customer",
                "branch",
                "managed_by"
            )
            .prefetch_related("items")
        )

        if not (
            user.is_superuser
            or user.role in ["SUPER_ADMIN", "ADMIN"]
        ):
            queryset = queryset.filter(
                branch_id=user.branch_id
            )

        return queryset


class OrderCreateAPIView(APIView):

    def post(self, request):
        serializer = OrderCreateSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        order = serializer.save()

        response_serializer = OrderResponseSerializer(order)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
