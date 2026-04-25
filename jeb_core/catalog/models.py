from django.db import models
from django.utils.text import slugify


class ComponentType(models.Model):
    name = models.CharField(max_length=75, unique=True)
    slug = models.CharField(max_length=75, unique=True, verbose_name='URL')
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class CpuList(models.Model):
    name = models.CharField(max_length=75, unique=True)
    slug = models.CharField(max_length=75, unique=True, verbose_name='URL')
    is_available = models.BooleanField(default=True, verbose_name="Доступен")
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class GpuList(models.Model):
    name = models.CharField(max_length=75, unique=True)
    slug = models.CharField(max_length=75, unique=True, verbose_name='URL')
    is_available = models.BooleanField(default=True, verbose_name="Доступен")
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
class RamList(models.Model):
    name = models.CharField(max_length=75, unique=True)
    slug = models.CharField(max_length=75, unique=True, verbose_name='URL')
    is_available = models.BooleanField(default=True, verbose_name="Доступен")
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
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

def get_default_computer_description():
    return {
        "short_spec": "Опишите предназначение сборки (например: Идеальное решение для 2K-гейминга и работы с графикой...)"
    }

class Computer(models.Model):
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        related_name='computers',
        verbose_name='Категория'
    )
    name = models.CharField(max_length=75, verbose_name='Название')
    slug = models.CharField(max_length=75, unique=True, verbose_name='URL')
    cpu = models.ForeignKey(
        CpuList, 
        on_delete=models.CASCADE,
        related_name='computers',
        verbose_name='Процессор'
    )
    gpu = models.ForeignKey(
        GpuList, 
        on_delete=models.CASCADE,
        related_name='computers',
        verbose_name='Видеокарта'
    )
    ram = models.ForeignKey(
        RamList, 
        on_delete=models.CASCADE,
        related_name='computers',
        verbose_name='Оперативная память'
    )
    pc_case = models.CharField(max_length=75, verbose_name='Корпус')
    power_unit = models.CharField(max_length=75, verbose_name='Блок питания')
    storage = models.CharField(max_length=75, verbose_name='Накопитель')
    description = models.JSONField(default=get_default_computer_description, verbose_name='Описание')
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

    @property
    def is_computer(self):
        return True


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

def get_default_description():
    return {
        "short_specs": {"info": "ИМЯ"},
        "full_info": {"architecture_details": "ИМЯ"}
    }

def get_default_specs():
    return {
        "tech": {
            "Бренд": "ИМЯ",
            "Модель": "ИМЯ",
            "Характеристика 1": "ИМЯ",
            "Характеристика 2": "ИМЯ"
        }
    }
class Component(models.Model):
    
    
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        related_name='components',
        verbose_name='Категория'
    )
    component_type = models.ForeignKey(
        ComponentType, 
        on_delete=models.CASCADE,
        related_name='components',
        verbose_name='Тип комплектующего'
    )
    name = models.CharField(max_length=75, verbose_name='Название')
    slug = models.CharField(max_length=75, unique=True, verbose_name='URL')

    specs = models.JSONField(default=get_default_specs, verbose_name='Характеристики')
    description = models.JSONField(default=get_default_description, verbose_name='Описание')

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
        return f"{self.name}"
    
    class Meta:
        verbose_name = 'Комплектующее'
        verbose_name_plural = 'Комплектующие'
        ordering = ['component_type', 'name']

    @property
    def is_computer(self):
        return False


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