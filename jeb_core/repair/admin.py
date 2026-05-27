from django.contrib import admin
from django.utils.html import format_html
from .models import RepairRequest

@admin.register(RepairRequest)
class RepairAdmin(admin.ModelAdmin):
    # Что отображаем в общей таблице заявок
    list_display = ['id', 'client_name', 'phone_number', 'device_type', 'status', 'estimated_cost', 'created_at', 'show_image_mini']
    
    # По каким полям можно кликнуть, чтобы перейти внутрь заявки
    list_display_links = ['id', 'client_name']
    
    # Правая панель быстрой фильтрации
    list_filter = ['status', 'device_type', 'created_at']
    
    # Живой поиск по ключевым данным
    search_fields = ['id', 'client_name', 'phone_number']
    
    # Возможность быстро менять статус и цену прямо из общего списка (мега-удобно!)
    list_editable = ['status', 'estimated_cost']
    
    # Управляем отображением полей внутри самой заявки (группируем для красоты)
    fieldsets = [
        ('Информация о клиенте', {
            'fields': ['user', 'client_name', 'phone_number']
        }),
        ('Детали неисправности', {
            'fields': ['device_type', 'description', 'image']
        }),
        ('Управление ремонтом (Для мастера)', {
            'fields': ['status', 'admin_comment', 'estimated_cost']
        }),
        ('Таймстампы', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse'] # Скроет даты под спойлер, чтобы не мешались
        }),
    ]
    
    # Даты создания теперь readonly, их нельзя поменять руками
    readonly_fields = ['created_at', 'updated_at']

    # Кастомное поле, чтобы прямо в таблице видеть маленькую иконку фотки, если она есть
    def show_image_mini(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 6px;" />', obj.image.url)
        return "Нет фото"
    
    show_image_mini.short_description = "Миниатюра"