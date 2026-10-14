from django.urls import path

from apps.orders import views

urlpatterns = [
    path("orders", views.OrderCreateView.as_view(), name="order-create"),
    path("orders/me", views.MyOrdersView.as_view(), name="order-me"),
    path("orders/<int:order_id>", views.OrderDetailView.as_view(), name="order-detail"),
    path(
        "payments/orders/<int:order_id>/pay",
        views.PayOrderView.as_view(),
        name="payment-pay",
    ),
    path(
        "payments/orders/<int:order_id>",
        views.OrderPaymentsView.as_view(),
        name="payment-list",
    ),
]
