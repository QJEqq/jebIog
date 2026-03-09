from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Client, Service, BuisnessAppeals, OrderChina, 
    CustomComputer, ProductImage
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


# 🌎 УСЛУГИ
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'icon', 'is_popular', 'is_active', 'sort_order']
    list_display_links = ['name']
    list_editable = ['is_popular', 'is_active', 'sort_order']
    search_fields = ['name', 'code', 'description']
    list_filter = ['is_popular', 'is_active']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    fieldsets = (
        ('Основное', {
            'fields': ('code', 'name', 'slug', 'icon', 'description')
        }),
        ('Настройки', {
            'fields': ('is_popular', 'is_active', 'sort_order')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# 📝 ЗАЯВКИ ОТ БИЗНЕСА
@admin.register(BuisnessAppeals)
class BuisnessAppealsAdmin(admin.ModelAdmin):
    list_display = ['name', 'company_name', 'phone', 'email', 'status', 'created_at']
    list_display_links = ['name']
    list_editable = ['status']
    list_filter = ['status', 'company_size', 'budget_range', 'timeline', 'created_at']
    search_fields = ['name', 'company_name', 'phone', 'email', 'project_description']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['service_type']
    
    fieldsets = (
        ('Контактная информация', {
            'fields': ('name', 'email', 'phone')
        }),
        ('О компании', {
            'fields': ('company_name', 'company_size', 'industry')
        }),
        ('Проект', {
            'fields': ('service_type', 'project_description', 'budget_range', 'timeline')
        }),
        ('Статус', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )


# 🇨🇳 ЗАКАЗЫ ИЗ КИТАЯ
@admin.register(OrderChina)
class OrderChinaAdmin(admin.ModelAdmin):
    list_display = [
        'tracking_number', 'client_link', 'goods_category', 
        'total_weight_kg', 'delivery_method', 'status', 
        'payment_status', 'created_at'
    ]
    list_display_links = ['tracking_number']
    list_editable = ['status', 'payment_status']
    list_filter = ['status', 'payment_status', 'delivery_method', 'is_fragile', 'created_at']
    search_fields = ['tracking_number', 'supplier_name', 'goods_description', 'client__name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['client']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Клиент', {
            'fields': ('client',)
        }),
        ('Отслеживание', {
            'fields': ('tracking_number', 'status', 'payment_status')
        }),
        ('Груз', {
            'fields': ('goods_description', 'goods_category', 'total_weight_kg', 
                      'total_volume_m3', 'quantity', 'is_fragile', 'insurance')
        }),
        ('Маршрут', {
            'fields': ('supplier_name', 'supplier_contacts', 'warehouse_from', 'delivery_to')
        }),
        ('Доставка', {
            'fields': ('delivery_method', 'pickup_date', 'estimated_arrival')
        }),
        ('Финансы', {
            'fields': ('declared_value_usd', 'delivery_cost_rub')
        }),
        ('Дополнительно', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def client_link(self, obj):
        if obj.client:
            url = reverse('admin:jeb_core_client_change', args=[obj.client.id])
            return format_html('<a href="{}">{}</a>', url, obj.client.name)
        return '-'
    client_link.short_description = 'Клиент'
    client_link.admin_order_field = 'client__name'


# 🖥️ КАСТОМНЫЕ ПК
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image']
    verbose_name = 'Дополнительное фото'
    verbose_name_plural = 'Дополнительные фото'


@admin.register(CustomComputer)
class CustomComputerAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'cpu', 'gpu', 'orm', 'price', 
        'quantity_in_stock', 'updated_at', 'created_at'
    ]
    list_display_links = ['name']
    list_editable = ['quantity_in_stock']
    list_filter = ['created_at']
    search_fields = ['name', 'cpu', 'gpu']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    inlines = [ProductImageInline]
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'slug')
        }),
        ('Комплектующие', {
            'fields': (
                'cpu', 'gpu',  'orm', 
                'storage', 'pc_case', 'power_unit'
            )
        }),
        ('Медиа', {
            'fields': ('main_image', 'description')
        }),
        ('Цены и наличие', {
            'fields': ('price', 'quantity_in_stock')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def price_display(self, obj):
        if obj.old_price:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">{}₽</span> <span style="color: #c41e3a; font-weight: bold;">{}₽</span>',
                 obj.price
            )
        return f"{obj.price}₽"
    price_display.short_description = 'Цена'
    price_display.admin_order_field = 'price'
    
    def ram(self, obj):
        return obj.orm if hasattr(obj, 'ram') else obj.orm
    ram.short_description = 'ОЗУ'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product']
    list_filter = ['product']
    raw_id_fields = ['product']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Превью'