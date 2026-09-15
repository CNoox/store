from django.contrib import admin
from .models import CategoryModel, ProductModel, ProductImageModel, AttributeModel, ProductVariantModel, StaticAttributeModel, VariantAttributeValueModel
from unfold.admin import ModelAdmin

# Register your models here.

@admin.register(CategoryModel)
class CategoryModelAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    exclude = ['slug']

@admin.register(ProductModel)
class ProductModelAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'description')
    exclude = ['slug']

@admin.register(ProductImageModel)
class ProductImageModelAdmin(ModelAdmin):
    list_display = ('image', 'product','id')

@admin.register(AttributeModel)
class ProductAttributeModelAdmin(ModelAdmin):
    list_display = ('key', 'type')


@admin.register(ProductVariantModel)
class ProductVariantModelAdmin(ModelAdmin):
    list_display = ('product', 'price', 'stock')


@admin.register(VariantAttributeValueModel)
class VariantAttributeValueModelAdmin(ModelAdmin):
    list_display = ('variant', 'attribute', 'label', 'value')

@admin.register(StaticAttributeModel)
class StaticAttributeModelAdmin(ModelAdmin):
    list_display = ('product', 'attribute', 'label', 'value')
