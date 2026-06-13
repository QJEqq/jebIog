from django.urls import path
from .views import CheckOutView, PaymentFailedView, PaymentSuccessView, PaymentCheckView
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', CheckOutView.as_view(), name='checkout'),
    path('payment/success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/failed/', PaymentFailedView.as_view(), name='payment_failed'),
    path('payment/check/', PaymentCheckView.as_view(), name='payment_check'),
    path('payment/webhook/yookassa/', views.yookassa_webhook , name='webhook'),
]