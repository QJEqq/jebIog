from django.contrib import admin
from .models import Category, Computer, ProductImage, Component, ComponentImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2

class ComponentImageInline(admin.TabularInline):
    model = ComponentImage
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'quantity_in_stock', 'is_available']
    list_filter = ['category', 'is_available']
    search_fields = ['name', 'cpu', 'gpu']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ]

@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ['name', 'component_type', 'category', 'price', 'quantity_in_stock']
    list_filter = ['component_type', 'category', 'is_available']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ComponentImageInline, ]