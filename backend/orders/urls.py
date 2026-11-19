
from django.urls import path

from .views import (
    OrderCreateAPIView,
    OrderListAPIView,
    OrderDetailAPIView,
)


urlpatterns = [
    path(
        "orders/",
        OrderListAPIView.as_view(),
        name="order-list"
    ),

    path(
        "orders/create/",
        OrderCreateAPIView.as_view(),
        name="order-create"
    ),

    path(
        "orders/<int:pk>/",
        OrderDetailAPIView.as_view(),
        name="order-detail"
    ),
]
