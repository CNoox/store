from django.contrib import admin
from .models import CategoryModel, ProductModel, ProductImageModel, ProductAttributeModel, AttributeValueModel
from unfold.admin import ModelAdmin

# Register your models here.

@admin.register(CategoryModel)
class CategoryModelAdmin(ModelAdmin):
    list_display = ('id','name', 'slug')
    exclude = ['slug']

@admin.register(ProductModel)
class ProductModelAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'description', 'base_price')
    exclude = ['slug']

@admin.register(ProductImageModel)
class ProductImageModelAdmin(ModelAdmin):
    list_display = ('image', 'product','id')

@admin.register(ProductAttributeModel)
class ProductAttributeModelAdmin(ModelAdmin):
    list_display = ('key', 'type', 'product')

@admin.register(AttributeValueModel)
class AttributeValueModelAdmin(ModelAdmin):
    list_display = ('label', 'value', 'attribute')