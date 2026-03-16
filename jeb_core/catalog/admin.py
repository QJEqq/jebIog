from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Computer , ProductImage

# 🖥️ КАСТОМНЫЕ ПК
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image']
    verbose_name = 'Дополнительное фото'
    verbose_name_plural = 'Дополнительные фото'

@admin.register(Computer)
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
# Register your models here.
