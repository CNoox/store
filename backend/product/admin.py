from django.contrib import admin
from .models import CategoryModel, ProductModel, ProductImageModel, AttributeModel, AttributeValueModel
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

@admin.register(AttributeValueModel)
class AttributeValueModelAdmin(ModelAdmin):
    list_display = ('attribute', 'value')

    def get_attribute(self, obj):
        return obj.attribute.key
