from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify/', views.verify_phone, name='verify_phone'),
    path('resend-sms/', views.resend_sms_view, name='resend_sms'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('account-details/', views.account_details, name='account_details'),
    path('edit-account-details/', views.edit_account_details, name='edit_account_details'),
    path('update-account-details/', views.update_account_details, name='update_account_details'),
    path('logout/', views.logout_view, name='logout'),
    path('order_history/', views.order_history, name='order_history'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    

]