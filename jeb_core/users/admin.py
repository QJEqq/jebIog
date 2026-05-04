from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    list_display = ('phone_number','first_name' , 'last_name', 'email' , 'country')
    list_filter = ('city',)
    search_fields = ('country', 'last_name', 'country', 'city')
    ordering = ('city',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Пеорсональная информация', {
            'fields': ('first_name', 'last_name',
                       'address', 'city', 'country', 'postal_code',
                       'email', 'discount_level')
        }),
        ('Информация доступов', {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions')
        }),
        ('Даты', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'first_name', 'last_name', 'password1',
                       'password2', 'is_staff', 'is_active'),
        }),
    )
admin.site.register(User, CustomUserAdmin)
    