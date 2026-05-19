from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # --- Authentication & Verification ---
    path('register/', views.register, name='register'),
    path('verify/', views.verify_phone, name='verify_phone'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # --- SMS Resending Control ---
    path('resend-sms/', views.resend_sms_view, name='resend_sms'),
    path('unresend-sms/', views.password_reset_resend_sms_view, name='resend_sms_un'),
    
    # --- Profile & Account Management ---
    path('profile/', views.profile_view, name='profile'),
    path('account-details/', views.account_details, name='account_details'),
    path('edit-account-details/', views.edit_account_details, name='edit_account_details'),
    path('update-account-details/', views.update_account_details, name='update_account_details'),
    
    # --- Order History & Payment ---
    path('order_history/', views.order_history, name='order_history'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('repay/<int:order_id>/', views.repay_order, name='repay_order'),
    
    # --- Password Reset Flow ---
    path('password-reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password-reset/confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),  
    path('profile/password-reset/init/', views.profile_password_reset_trigger_view, name='profile_password_reset_init'),
]