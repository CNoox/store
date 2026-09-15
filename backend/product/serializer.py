import json

from django.db import transaction

from rest_framework import serializers

from .models import (
    VariantAttributeValueModel,
    AttributeModel,
    ProductImageModel,
    ProductModel,
    CategoryModel,
    ProductVariantModel,
    StaticAttributeModel
)


class JSONListField(serializers.ListField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                raise serializers.ValidationError('Must be a valid JSON.')

        if isinstance(data, list) and len(data) == 1 and isinstance(data[0], str):
            try:
                data = json.loads(data[0])
            except json.JSONDecodeError:
                raise serializers.ValidationError('Must be a valid JSON.')

        return super().to_internal_value(data)


class CategorySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField()
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = CategoryModel
        fields = ['id', 'name', 'slug']


class CategoryField(serializers.RelatedField):
    queryset = CategoryModel.objects.all()

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(name=data)
        except CategoryModel.DoesNotExist:
            raise serializers.ValidationError('Category Not Found.')

    def to_representation(self, value):
        return CategorySerializer(value).data


class VariantAttributeValueSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    attribute = serializers.CharField(source='attribute.key')
    attribute_type = serializers.CharField(source='attribute.type')

    class Meta:
        model = VariantAttributeValueModel
        fields = ['id', 'attribute', 'attribute_type', 'label', 'value']


class VariantAttributeValueWriteSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=100)
    type = serializers.ChoiceField(choices=AttributeModel.TypeChoices.choices)
    label = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    value = serializers.CharField(max_length=100)


class ProductVariantSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    variant_is_available = serializers.SerializerMethodField(read_only=True)
    attributes = VariantAttributeValueSerializer(source='variant_attributes', many=True, read_only=True)

    class Meta:
        model = ProductVariantModel
        fields = ['id', 'price', 'stock', 'variant_is_available', 'attributes']

    def get_variant_is_available(self, obj):
        return obj.stock > 0


class ProductVariantWriteSerializer(serializers.ModelSerializer):
    attributes = JSONListField(child=VariantAttributeValueWriteSerializer())

    class Meta:
        model = ProductVariantModel
        fields = ['price', 'stock', 'attributes']


class ProductImageSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    image = serializers.ImageField()
    alt = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProductImageModel
        fields = ['id', 'image', 'alt']

    def get_alt(self, obj):
        return obj.product.name


class StaticAttributeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    attribute = serializers.CharField(source='attribute.key')
    attribute_type = serializers.CharField(source='attribute.type')

    class Meta:
        model = StaticAttributeModel
        fields = ['id', 'product_id', 'attribute', 'attribute_type', 'label', 'value']


class StaticAttributeWriteSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=100)
    type = serializers.ChoiceField(choices=AttributeModel.TypeChoices.choices)
    label = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    value = serializers.CharField(max_length=100)


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    category = CategoryField()
    images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    variants = JSONListField(child=ProductVariantWriteSerializer(), write_only=True, required=False)
    static_attributes = JSONListField(child=StaticAttributeWriteSerializer(), write_only=True, required=False)

    class Meta:
        model = ProductModel
        fields = ['id', 'name', 'slug', 'description', 'category', 'images', 'variants', 'static_attributes']

    def validate(self, attrs):
        if not self.instance and not attrs.get('images'):
            request = self.context.get('request')

            if not request or not request.FILES.getlist('images'):
                raise serializers.ValidationError({
                    'images': 'At least one image is required.'
                })

        return attrs

    def get_attribute(self, attribute_data):
        key = attribute_data['key']
        attribute_type = attribute_data['type']

        try:
            attribute = AttributeModel.objects.get(key=key)
        except AttributeModel.DoesNotExist:
            raise serializers.ValidationError({
                'attribute': f'Attribute "{key}" does not exist.'
            })

        if attribute.type != attribute_type:
            raise serializers.ValidationError({
                'attribute': f'Attribute "{key}" has type "{attribute.type}", not "{attribute_type}".'
            })

        return attribute

    def create_variant_attributes(self, variant, attributes):
        for attribute_data in attributes:
            attribute = self.get_attribute(attribute_data)

            VariantAttributeValueModel.objects.create(
                variant=variant,
                attribute=attribute,
                label=attribute_data.get('label'),
                value=attribute_data['value']
            )

    def create_static_attributes(self, product, attributes):
        for attribute_data in attributes:
            attribute = self.get_attribute(attribute_data)

            StaticAttributeModel.objects.create(
                product=product,
                attribute=attribute,
                label=attribute_data.get('label'),
                value=attribute_data['value']
            )

    @transaction.atomic
    def create(self, validated_data):
        images = validated_data.pop('images', [])
        variants = validated_data.pop('variants', [])
        static_attributes = validated_data.pop('static_attributes', [])

        product = ProductModel.objects.create(**validated_data)

        for image in images:
            ProductImageModel.objects.create(product=product, image=image)

        for variant_data in variants:
            attributes = variant_data.pop('attributes', [])
            variant = ProductVariantModel.objects.create(product=product, **variant_data)
            self.create_variant_attributes(variant, attributes)

        self.create_static_attributes(product, static_attributes)

        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        images = validated_data.pop('images', [])
        variants = validated_data.pop('variants', None)
        static_attributes = validated_data.pop('static_attributes', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        for image in images:
            ProductImageModel.objects.create(product=instance, image=image)

        if variants is not None:
            instance.variants.all().delete()

            for variant_data in variants:
                attributes = variant_data.pop('attributes', [])
                variant = ProductVariantModel.objects.create(product=instance, **variant_data)
                self.create_variant_attributes(variant, attributes)

        if static_attributes is not None:
            instance.static_attributes.all().delete()
            self.create_static_attributes(instance, static_attributes)

        return instance


class AllProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    category = serializers.CharField(source='category.name')
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    product_is_available = serializers.SerializerMethodField(read_only=True)
    static_attributes = StaticAttributeSerializer(many=True, read_only=True)

    class Meta:
        model = ProductModel
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'category',
            'images',
            'variants',
            'static_attributes',
            'product_is_available'
        ]

    def get_product_is_available(self, obj):
        return obj.variants.filter(stock__gt=0).exists()


class AttributeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = AttributeModel
        fields = ['id', 'key', 'type']


# ==================================

class ProductPaginationSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = AllProductSerializer(many=True)
