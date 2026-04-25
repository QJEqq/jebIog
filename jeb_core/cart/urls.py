from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
     path('add/<str:item_type>/<int:product_id>/' , views.cart_add , name='add'),
     path('' , views.cart_detail , name='cart_detail'),
     path('count/', views.cart_count, name='cart_count'),

]