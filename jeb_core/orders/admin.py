from django.contrib import admin
from .models import Order, OrderItem
from django.utils.safestring import mark_safe

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('image_preview', 'get_item_name', 'quantity', 'price', 'get_total_price')
    readonly_fields = ('image_preview', 'get_item_name', 'get_total_price')
    can_delete = False

    def image_preview(self, obj):
        item = obj.component or obj.computer
        if item and item.main_image:
            return mark_safe(f'<img src="{item.main_image.url}" style="max-height: 80px; border-radius: 8px;" />')
        return mark_safe('<span style="color: gray;">Нет фото</span>')
    image_preview.short_description = 'Фото'

    def get_item_name(self, obj):
        if obj.component:
            return f"🔧 {obj.component.name} (Комплектующее)"
        if obj.computer:
            return f"🖥️ {obj.computer.name} (Сборка)"
        return "Товар удален"
    get_item_name.short_description = 'Товар'

    def get_total_price(self, obj):
        try:
            return obj.get_total_price
        except:
            return mark_safe('<span style="color: red;">Invalid Data</span>')
    get_total_price.short_description = 'Сумма товаров'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_name', 'total_price', 'status', 'created_at']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    
    # Базовые поля только для чтения
    readonly_fields = ('created_at', 'updated_at', 'total_price')

    fieldsets = (
        ('Клиент и доставка', {
            'fields': (
                'user', 
                ('first_name', 'last_name'), 
                'email', 
                'phone_number', 
                'city', 
                'address', 
                'postal_code'
            )
        }),
        ('Детали заказа', {
            'fields': (
                'status', 
                'total_price', 
            )
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',), # Эта секция будет свернута по умолчанию
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj: # При редактировании блокируем всё, кроме статуса
            return self.readonly_fields + (
                'user', 'first_name', 'last_name', 'email', 
                'phone_number', 'city', 'address', 'postal_code'
            )
        return self.readonly_fields
