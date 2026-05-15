from django.db import models
from django.conf import settings
from catalog.models import Component, Computer
from phonenumber_field.modelfields import PhoneNumberField

class Order(models.Model):
    STATUS_CHOISES = (
        ('pending' , 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('processing', 'Сборка заказа'),
        ('shipped', 'Передан в доставку'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
        )
    
    # Личные данные

    phone_number = PhoneNumberField(
        region='RU',  
        verbose_name='Номер телефона'
    )
    email = models.EmailField( max_length=254, verbose_name='Электронная почта')
    first_name = models.CharField(max_length=35, verbose_name='Имя')
    last_name = models.CharField(max_length=35, verbose_name='Фамилия')

    # Адрес доставки

    city = models.CharField(max_length=35, blank=True, null=True, verbose_name='Город')
    address = models.TextField(blank=True, null=True, verbose_name="Адрес доставки")
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name='Почтовый Индекс')

    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Общая стоимость')
    status = models.CharField(max_length=20, choices=STATUS_CHOISES, default='pending', verbose_name='Статус')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления')

    class Meta:
        verbose_name = 'Заказ'
        
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ №{self.id} | Номер: {self.phone_number}'
    
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE,
        related_name='items'
    )

    component = models.ForeignKey(Component, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Комплектующее')
    computer = models.ForeignKey(Computer, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Компьютеры')

    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Цена при покупке')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    def get_total_price(self):
        return self.price * self.quantity
    
    def __str__(self):
        item = self.component or self.computer
        if item:
            return f"{item.name} x {self.quantity}"
        return "Новая позиция"
    
    @property
    def item(self):
        return self.component or self.computer
    
