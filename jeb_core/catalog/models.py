from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=75, unique=True, verbose_name='Название')
    slug = models.CharField(max_length=75, unique=True, verbose_name='URL')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']


class Computer(models.Model):
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        related_name='computers',
        verbose_name='Категория'
    )
    name = models.CharField(max_length=75, verbose_name='Название')
    slug = models.CharField(max_length=75, unique=True, verbose_name='URL')
    cpu = models.CharField(max_length=55, verbose_name='Процессор')
    gpu = models.CharField(max_length=125, verbose_name='Видеокарта')
    ram = models.CharField(max_length=75, verbose_name='Оперативная память') 
    pc_case = models.CharField(max_length=75, verbose_name='Корпус')
    power_unit = models.CharField(max_length=75, verbose_name='Блок питания')
    storage = models.CharField(max_length=75, verbose_name='Накопитель')
    description = models.JSONField(default=dict, verbose_name='Описание')
    main_image = models.ImageField(upload_to='customPC/main/', verbose_name='Главное фото')
    price = models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Цена')
    created_at = models.DateField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateField(auto_now=True, verbose_name='Обновлен')
    quantity_in_stock = models.PositiveIntegerField(default=1, verbose_name='В наличии (шт)')
    is_available = models.BooleanField(default=True, verbose_name='Доступен')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Компьютер'
        verbose_name_plural = 'Компьютеры'
        ordering = ['-created_at']


class ProductImage(models.Model):
    product = models.ForeignKey(
        Computer, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name='Компьютер'
    )
    image = models.ImageField(upload_to='customPC/extra/', verbose_name='Фото')
    
    class Meta:
        verbose_name = 'Фото компьютера'
        verbose_name_plural = 'Фото компьютеров'


class Component(models.Model):
    class ComponentType(models.TextChoices):
        CPU = 'cpu', 'Процессор'
        GPU = 'gpu', 'Видеокарта'
        RAM = 'ram', 'Оперативная память'
        STORAGE = 'storage', 'Накопитель'
        POWER = 'power', 'Блок питания'
        CASE = 'case', 'Корпус'
        COOLING = 'cooling', 'Охлаждение'
    
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        related_name='components',
        verbose_name='Категория'
    )
    component_type = models.CharField(
        max_length=20,
        choices=ComponentType.choices,
        default=ComponentType.CPU,
        verbose_name='Тип комплектующего'
    )
    name = models.CharField(max_length=75, verbose_name='Название')
    slug = models.CharField(max_length=75, unique=True, verbose_name='URL')
    specs = models.JSONField(default=dict, verbose_name='Характеристики')
    description = models.JSONField(default=dict, verbose_name='Описание')
    main_image = models.ImageField(upload_to='component/main/', verbose_name='Главное фото')
    price = models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Цена')
    created_at = models.DateField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateField(auto_now=True, verbose_name='Обновлен')
    quantity_in_stock = models.PositiveIntegerField(default=1, verbose_name='В наличии (шт)')
    is_available = models.BooleanField(default=True, verbose_name='Доступен')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_component_type_display()}: {self.name}"
    
    class Meta:
        verbose_name = 'Комплектующее'
        verbose_name_plural = 'Комплектующие'
        ordering = ['component_type', 'name']


class ComponentImage(models.Model):
    component = models.ForeignKey(
        Component, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name='Комплектующее'
    )
    image = models.ImageField(upload_to='component/extra/', verbose_name='Фото')
    
    class Meta:
        verbose_name = 'Фото комплектующего'
        verbose_name_plural = 'Фото комплектующих'