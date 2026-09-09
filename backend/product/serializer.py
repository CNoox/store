from rest_framework import serializers
from .models import AttributeValueModel,ProductAttributeModel,ProductImageModel,ProductModel,CategoryModel

class CategorySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField()
    local_name = serializers.CharField()
    slug = serializers.SlugField(read_only=True)
    class Meta:
        model = CategoryModel
        fields = ['id', 'name', 'slug', 'local_name']

class AttributeValueSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    price_modifier_percent = serializers.IntegerField(required=True)
    class Meta:
        model = AttributeValueModel
        fields = ["id", "label", "value","price_modifier_percent"]

class ProductAttributeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    values = AttributeValueSerializer(many=True)
    class Meta:
        model = ProductAttributeModel
        fields = ["id", "key", "type", "is_selective", "values"]

class ProductImageSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    image = serializers.ImageField()
    alt = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = ProductImageModel
        fields = ["id", "image", "alt"]
    def get_alt(self, obj):
        return obj.product.name


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    category = serializers.CharField()
    stock = serializers.IntegerField(required=True)
    attribute_list = ProductAttributeSerializer(source='attributes',many=True)
    base_price = serializers.IntegerField(required=True)
    discount_percent = serializers.IntegerField(required=True)
    class Meta:
        model = ProductModel
        fields = ["id","name","description","stock","base_price","discount_percent","category","attribute_list"]
    def validate_stock(self, obj):
        if obj >= 100000:
            raise serializers.ValidationError('is very big integer must be less than 6 digit.')
        return obj
    def validate_base_price(self, obj):
        if obj >= 10000000000:
            raise serializers.ValidationError('is very big integer must be less than 11 digit.')
        return obj

    def validate_discount_percent(self, obj):
        if obj >= 100:
            raise serializers.ValidationError('is very big integer must be less than 3 digit.')
        return obj

class AllProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    category = serializers.CharField(source='category.name')
    category_label = serializers.CharField(source='category.local_name')
    description = serializers.CharField()
    stock = serializers.IntegerField(min_value=0)
    base_price = serializers.IntegerField(min_value=0)
    discount_percent = serializers.IntegerField(default=0, min_value=0)
    images = ProductImageSerializer(many=True)
    is_available = serializers.SerializerMethodField(read_only=True)
    attribute_list = ProductAttributeSerializer(source='attributes',many=True)

    def get_is_available(self,obj):
        return obj.stock > 0

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance