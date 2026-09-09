from django.db import models
from django.utils.text import slugify

# Create your models here.

class ProductModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=150, unique=True,null=True,blank=True)
    category = models.ForeignKey('CategoryModel', on_delete=models.CASCADE)
    description = models.TextField()
    stock = models.PositiveIntegerField(default=0)
    base_price = models.PositiveBigIntegerField(default=0)
    discount_percent = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.pk:
            old_product = ProductModel.objects.get(pk=self.pk)
            if old_product.name != self.name:
                self.slug = slugify(self.name,allow_unicode=True)
        else:
            self.slug = slugify(self.name,allow_unicode=True)
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

class ProductAttributeModel(models.Model):
    class KeyChoices(models.TextChoices):
        SIZE = 'size','سایز'
        COLOR = 'color','رنگ'
        MATERIAL = 'material','جنس'

    class TypeChoices(models.TextChoices):
        COLOR = 'color','رنگ'
        TEXT = 'text','متن'

    key = models.CharField(max_length=100, choices=KeyChoices.choices)
    type = models.CharField(max_length=100, choices=TypeChoices.choices)
    is_selective = models.BooleanField()
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='attributes')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product', 'key'], name='unique_product_attribute')
        ]

    def __str__(self):
        return f'{self.key} - {self.type}'

class AttributeValueModel(models.Model):
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    price_modifier_percent = models.IntegerField(default=0)
    attribute = models.ForeignKey(ProductAttributeModel, on_delete=models.CASCADE, related_name='values')

    def __str__(self):
        return f'{self.label} - {self.value}'

class CategoryModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=150, unique=True,null=True,blank=True)
    local_name = models.CharField(max_length=200, unique=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old_category = CategoryModel.objects.get(pk=self.pk)
            if old_category.name != self.name:
                self.slug = slugify(self.name,allow_unicode=True)
        else:
            self.slug = slugify(self.name,allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.local_name} - {self.name}'
