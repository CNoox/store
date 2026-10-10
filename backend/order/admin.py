from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import OrderModel,CartModel,AddressModel

# Register your models here.

@admin.register(OrderModel)
class OrderModelAdmin(ModelAdmin):
    list_display = ['id','user','total_price','status',]

@admin.register(CartModel)
class CartModelAdmin(ModelAdmin):
    list_display = ['id','user',]

@admin.register(AddressModel)
class AddressModelAdmin(ModelAdmin):
    list_display = ['id','order','address',]
