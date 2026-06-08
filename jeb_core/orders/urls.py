from django.urls import path
from .views import CheckOutView, PaymentFailedView, PaymentSuccessView

app_name = 'orders'

urlpatterns = [
    path('checkout/', CheckOutView.as_view(), name='checkout'),
    path('payment/success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/failed/', PaymentFailedView.as_view(), name='payment_failed'),
]