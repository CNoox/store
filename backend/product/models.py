from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError

# Create your models here.

class ProductModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=150, unique=True, null=True, blank=True)
    category = models.ForeignKey('CategoryModel', on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    base_price = models.PositiveBigIntegerField(default=0)
    discounted_price = models.PositiveBigIntegerField(blank=True, null=True)
    stock = models.PositiveSmallIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.pk:
            old_product = ProductModel.objects.get(pk=self.pk)
            if old_product.name != self.name:
                self.slug = slugify(self.name, allow_unicode=True)
        else:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name

def product_image_path(instance, filename):
    return f'products/{instance.product.name}/{filename}'
class ProductImageModel(models.Model):
    image = models.ImageField(upload_to=product_image_path)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return self.product.name

class AttributeModel(models.Model):
    class TypeChoices(models.TextChoices):
        COLOR = 'color', 'رنگ'
        TEXT = 'text', 'متن'

    key = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=100, choices=TypeChoices.choices)

    def __str__(self):
        return f'{self.key}'

class AttributeValueModel(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='values')
    attribute = models.ForeignKey(AttributeModel, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['attribute', 'product','value'],name='unique_product_attribute_value')]
    def __str__(self):
        return f'{self.attribute}'



class CategoryModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=150, unique=True,null=True,blank=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old_category = CategoryModel.objects.get(pk=self.pk)
            if old_category.name != self.name:
                self.slug = slugify(self.name,allow_unicode=True)
        else:
            self.slug = slugify(self.name,allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name