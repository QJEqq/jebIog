from django.db import models
from django.utils.text import slugify

class Computer(models.Model):
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
    product = models.ForeignKey(Computer, on_delete=models.CASCADE, 
                                related_name='images')
    image = models.ImageField(upload_to='customPC/extra/')
