from django.contrib import admin

from .models import (
    Client
)

# 👨‍🦱 КЛИЕНТЫ
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'email', 'tg_id', 'created_at']
    list_display_links = ['name']
    search_fields = ['name', 'phone_number', 'email', 'tg_id']
    list_filter = ['created_at']
    readonly_fields = ['slug', 'tg_id', 'created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'email', 'phone_number')
        }),
        ('Telegram', {
            'fields': ('tg_id',),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )



