from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField

class RepairRequest(models.Model):
    DEVICE_CHOICES = [
        ('pc', 'Стационарный ПК'),
        ('laptop', 'Ноутбук'),
        ('gpu', 'Видеокарта'),
        ('other', 'Другое железо'),
    ]

    STATUS_CHOICES = [
        ('new', 'Новая заявка'),
        ('diagnostic', 'Диагностика'),
        ('in_progress', 'В работе'),
        ('ready', 'Готов к выдаче'),
        ('completed', 'Завершен'),
        ('canceled', 'Отменен'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='JEB ID'

    )
    phone_number = PhoneNumberField(
        unique=False,
        region='RU',  
        verbose_name='Номер телефона'
    )
    client_name = models.CharField(max_length=75, verbose_name='Имя клиента')

    device_type = models.CharField(max_length=20, choices=DEVICE_CHOICES, default='pc', verbose_name='Тип устройства')
    description = models.TextField(verbose_name='Описание работы')
    image = models.ImageField(upload_to='repairs/%Y/%m', blank=True, null=True, verbose_name='Фото устройства')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_comment = models.TextField(blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Стоимость ремонта")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Заявка на ремонт"
        verbose_name_plural = "Заявки на ремонт"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка #{self.id} — {self.client_name} ({self.get_status_display()})"