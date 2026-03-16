from django.db import models
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from jeb_core.utils.telegram_utils import get_telegram_id 

# 👨‍🦱 КЛИЕНТ  👨‍🦱

class Client(models.Model):
    name = models.CharField(max_length=75)
    slug = models.CharField(max_length=75, unique=True)
    email = models.EmailField(max_length=254, unique=True, blank=True)
    phone_number = PhoneNumberField(
        unique=True,
        region='RU',  
        verbose_name='Номер телефона'
    )
    tg_id = models.CharField(unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        if self.phone_number and not self.tg_id:
            try:
                result = get_telegram_id(self.phone_number)
                if result.get('found'):
                    self.tg_id = result['tg_id']

            except Exception as e:
                import logging 
                logger = logging.getLogger(__name__)
                logger.error(f'не удалось найти телеграм id {e}')
        super().save(*args, **kwargs)

    
    def __str__(self):
        return self.name



