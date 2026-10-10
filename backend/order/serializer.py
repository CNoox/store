from rest_framework import serializers
from .models import OrderModel
from account.models import ProfileModel

class ProfileOrderSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    class Meta:
        model = ProfileModel
        fields = ['name','email']

    def get_name(self, obj):
        return f"{obj.first_name or ''} {obj.last_name or ''}".strip()

    def get_email(self, obj):
        return obj.user.email

class OrderSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    class Meta:
        model = OrderModel
        fields = ['order_number','name','email','status','total_price','created_at','updated_at']

    def get_name(self, obj):
        try:
            obj.user.profile
        except:
            return ''
        return f"{obj.user.profile.first_name} {obj.user.profile.last_name}"

    def get_email(self, obj):
        return obj.user.email


class PaginateOrderSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = OrderSerializer(many=True, read_only=True)


class SelectOrderSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    class Meta:
        model = OrderModel
        fields = ['order_number','name','email','status','items','total_price','created_at','updated_at','address','phone_number']

    def get_name(self, obj):
        try:
            obj.user.profile
        except:
            return ''
        return f"{obj.user.profile.first_name} {obj.user.profile.last_name}"

    def get_email(self, obj):
        return obj.user.email

    def get_address(self, obj):
        return obj.address.address

    def get_phone_number(self, obj):
        return obj.address.phone_number

class PaginateSelectOrderSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = SelectOrderSerializer(many=True, read_only=True)
