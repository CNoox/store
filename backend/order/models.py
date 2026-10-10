from django.db import models
from account.models import UserModel
from product.models import ProductModel
from django.core.validators import MinValueValidator
import secrets

# Create your models here.

class CartModel(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE,related_name='cart')

    def __str__(self):
        return f"Cart #{self.pk} - {self.user}"

class CartItemModel(models.Model):
    cart = models.ForeignKey(CartModel,on_delete=models.CASCADE,related_name="items",)
    product = models.ForeignKey(ProductModel,on_delete=models.CASCADE,related_name="cart_items",)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = [models.UniqueConstraint(fields=["cart", "product"],name="unique_product_per_cart",)]



class OrderModel(models.Model):
    class Status(models.TextChoices):
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    order_number = models.CharField(max_length=20, unique=False, editable=False)
    user = models.ForeignKey(UserModel,on_delete=models.CASCADE,related_name="orders",)
    status = models.CharField(max_length=20,choices=Status.choices,)
    total_price = models.CharField()
    items = models.JSONField(default=list,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{secrets.token_hex(6).upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.pk}"

class AddressModel(models.Model):
    order = models.OneToOneField(OrderModel, on_delete=models.CASCADE,related_name="address")
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=11)

    def __str__(self):
        return f'{self.address} - {self.phone_number}'
