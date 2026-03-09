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

#🌎 ЭКОСИСТЕМА БИЗНЕСА 🌎

class Service(models.Model):
    code = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name='Код',
        help_text='Уникальный идентификатор'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )

    slug = models.CharField(max_length=100, unique=True)
    
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Иконка (emoji)',
        help_text='Например: 🌐, 📱, 🤖'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание',
        help_text='Коротко о услуге (для карточки на сайте)'
    )
    
    # Настройки отображения
    is_popular = models.BooleanField(
        default=False,
        verbose_name='Популярная',
        help_text='Показывать в блоке "Популярные услуги"'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна',
        help_text='Отображать на сайте'
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок сортировки'
    )
    
    # Мета-информация
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    
    def __str__(self):
        icon = self.icon if self.icon else '📌'
        return f"{icon} {self.name}"
        
class BuisnessAppeals(models.Model): 
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    company_name = models.CharField(max_length=200, verbose_name="Название компании")
    company_size = models.CharField(max_length=50, choices=[
        ('small', 'Малый бизнес (1-10 человек)'),
        ('medium', 'Средний бизнес (11-50 человек)'),
        ('large', 'Крупный бизнес (50+ человек)'),
    ], verbose_name="Размер компании")
    industry = models.CharField(max_length=100, verbose_name="Сфера деятельности")
    service_type = models.ManyToManyField(Service,
                                          blank=True)
    project_description = models.TextField(verbose_name="Описание проекта")
    budget_range = models.CharField(max_length=50, choices=[
        ('under_100k', 'До 100 000 руб'),
        ('100k_500k', '100 000 - 500 000 руб'),
        ('500k_1m', '500 000 - 1 млн руб'),
        ('1m_plus', 'Более 1 млн руб'),
    ], verbose_name="Бюджет")
    timeline = models.CharField(max_length=50, choices=[
        ('urgent', 'Срочно (1-2 недели)'),
        ('fast', 'Быстро (1 месяц)'),
        ('normal', 'Обычно (2-3 месяца)'),
        ('flexible', 'Гибкие сроки'),
    ], verbose_name="Сроки")

    status = models.CharField(max_length=20, choices=[
        ('new', 'Новая'),
        ('review', 'На рассмотрении'),
        ('contacted', 'Связались'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
    ], default='new', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company_name}"
    
    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

# ОПТОВЫЕ ДОСТАВКИ ИЗ КИТАЯ

class OrderChina(models.Model):
    
    class DeliveryMethod(models.TextChoices):
        SEA = 'sea', 'Море (контейнер)'
        AIR = 'air', 'Авиа'
        RAIL = 'rail', 'Ж/д'
        EXPRESS = 'express', 'Экспресс-доставка (DHL/FedEx)'
        CARGO = 'cargo', 'Сборный груз'
    
    class PaymentStatus(models.TextChoices):
        NOT_PAID = 'not_paid', 'Не оплачен'
        PARTIAL = 'partial', 'Частично оплачен'
        PAID = 'paid', 'Оплачен'
        REFUND = 'refund', 'Возврат'
    
    class OrderStatus(models.TextChoices):
        NEW = 'new', 'Новая заявка'
        PROCESSING = 'processing', 'В обработке'
        PURCHASING = 'purchasing', 'Закупка товара'
        STORAGE = 'storage', 'На складе в Китае'
        IN_TRANSIT = 'in_transit', 'В пути'
        CUSTOMS = 'customs', 'На таможне'
        IN_RUSSIA = 'in_russia', 'В России'
        DELIVERED = 'delivered', 'Доставлен'
        CANCELLED = 'cancelled', 'Отменён'
    
    client = models.ForeignKey(
        Client, 
        on_delete=models.PROTECT,
        related_name='china_orders',
        verbose_name='Клиент'
    )
    
    tracking_number = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name='Трек-номер',
        help_text='Уникальный номер заказа/трека'
    )
    
    goods_description = models.TextField(
        verbose_name='Описание товара',
        help_text='Что именно везём? (Например: "Электроника: наушники 50шт")'
    )
    goods_category = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Категория товара',
        help_text='Например: электроника, одежда, запчасти'
    )
    
    total_weight_kg = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Общий вес (кг)'
    )
    total_volume_m3 = models.DecimalField(
        max_digits=10, 
        decimal_places=3,
        blank=True, 
        null=True,
        verbose_name='Объём (м³)'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество мест'
    )
    
    supplier_name = models.CharField(
        max_length=200,
        verbose_name='Поставщик',
        help_text='Название компании/магазина в Китае'
    )
    supplier_contacts = models.TextField(
        blank=True,
        verbose_name='Контакты поставщика'
    )
    warehouse_from = models.CharField(
        max_length=200,
        default='Гуанчжоу',
        verbose_name='Склад в Китае',
        help_text='Город или адрес склада'
    )
    delivery_to = models.CharField(
        max_length=200,
        verbose_name='Адрес доставки в РФ',
        help_text='Город и адрес получателя'
    )
    
    delivery_method = models.CharField(
        max_length=20,
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.CARGO,
        verbose_name='Способ доставки'
    )
    
    declared_value_usd = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name='Декларируемая стоимость ($)',
        help_text='Для страховки и таможни'
    )
    delivery_cost_rub = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        blank=True, 
        null=True,
        verbose_name='Стоимость доставки (₽)'
    )
    
    # ДАТЫ
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата заявки'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено'
    )
    pickup_date = models.DateField(
        blank=True, 
        null=True,
        verbose_name='Плановая дата забора'
    )
    estimated_arrival = models.DateField(
        blank=True, 
        null=True,
        verbose_name='Планируемая дата прибытия'
    )
    
    # СТАТУСЫ
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
        verbose_name='Статус заказа'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.NOT_PAID,
        verbose_name='Статус оплаты'
    )
    
    # ДОПОЛНИТЕЛЬНО (опционально, но полезно)
    notes = models.TextField(
        blank=True,
        verbose_name='Примечания',
        help_text='Особые отметки, нюансы доставки'
    )
    is_fragile = models.BooleanField(
        default=False,
        verbose_name='Хрупкий груз'
    )
    insurance = models.BooleanField(
        default=False,
        verbose_name='Нужна страховка'
    )
    
    def __str__(self):
        return f"Заказ {self.tracking_number} - {self.client.name}"
    
    class Meta:
        verbose_name = 'Заказ из Китая'
        verbose_name_plural = 'Заказы из Китая'
        indexes = [
            models.Index(fields=['tracking_number']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]

# КАСТОМ СБОРКИ ПК

class CustomComputer(models.Model):
    name = models.CharField(max_length=75)
    slug = models.CharField(max_length=75 , unique=True)
    cpu = models.CharField(max_length=55)
    gpu = models.CharField(max_length=125)
    orm = models.CharField(max_length=75)
    pc_case = models.CharField(max_length=75)
    power_unit = models.CharField(max_length=75)
    storage = models.CharField(max_length=75)
    description = models.JSONField()
    main_image = models.ImageField(upload_to='customPC/main/')
    price = models.DecimalField(decimal_places=2, max_digits=12)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    quantity_in_stock = models.PositiveIntegerField(
        default=1,
        verbose_name='В наличии (шт)'
    )
    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    product = models.ForeignKey(CustomComputer, on_delete=models.CASCADE, 
                                related_name='images')
    image = models.ImageField(upload_to='customPC/extra/')