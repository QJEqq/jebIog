
from django.contrib.auth.models import AbstractUser , BaseUserManager
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.html import strip_tags

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number ,  first_name, last_name , password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Номер телефона должен быть задан')
        if 'email' in extra_fields:
             extra_fields['email'] = self.normalize_email(extra_fields['email'])
        user =  self.model(phone_number=phone_number, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number ,  first_name, last_name , password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phone_number, first_name, last_name, password, **extra_fields)


class User(AbstractUser):
    username = None

    phone_number = PhoneNumberField(
        unique=True,
        region='RU',  
        verbose_name='Номер телефона'
    )
    email = models.EmailField(unique=True, max_length=254)
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)
   

    city = models.CharField(max_length=35, blank=True, null=True)
    province = models.CharField(max_length=35, blank=True, null=True)
    address = models.TextField(blank=True, null=True, verbose_name="Адрес доставки")
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    discount_level = models.IntegerField(default=0, verbose_name="Процент скидки")

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    def clean(self):
        for field in ['email', 'city', 'province', 'address', 'postal_code', 'discount_level']:
            value = getattr(self, field)
            if value:
                setattr(self,field, strip_tags(value))

    def __str__(self):
        return str(self.phone_number)