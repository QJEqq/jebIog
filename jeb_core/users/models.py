
from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
class User(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, blank=True, null=True, verbose_name="Telegram ID")
    telegram_username = models.CharField(max_length=100, blank=True, null=True, verbose_name="Username TG")
    is_tg_verified = models.BooleanField(default=False)
    phone_number = PhoneNumberField(
        unique=True,
        region='RU',  
        verbose_name='Номер телефона'
    )
    address = models.TextField(blank=True, null=True, verbose_name="Адрес доставки")
    
    discount_level = models.IntegerField(default=0, verbose_name="Процент скидки")

    def __str__(self):
        return self.username