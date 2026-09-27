import json
from django.db import transaction
from rest_framework import serializers
from .models import (
    AttributeModel,
    AttributeValueModel,
    ProductImageModel,
    ProductModel,
    CategoryModel,
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
        return value.slug


class AttributeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = AttributeModel
        fields = ['id', 'key', 'type']


class ProductImageSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    url = serializers.SerializerMethodField()
    alt = serializers.SerializerMethodField()

    class Meta:
        model = ProductImageModel
        fields = ['id', 'url', 'alt']

    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    def get_alt(self, obj):
        return obj.product.name


class AttributeWriteSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=100)
    type = serializers.ChoiceField(choices=AttributeModel.TypeChoices.choices,read_only=True)
    values = serializers.ListField(child=serializers.CharField(max_length=100))


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    category = CategoryField()
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
    )
    attribute_list = JSONListField(
        child=AttributeWriteSerializer(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = ProductModel
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'category',
            'base_price',
            'discounted_price',
            'stock',
            'images',
            'attribute_list',
        ]

    def validate(self, attrs):
        if not self.instance and not attrs.get('images'):
            request = self.context.get('request')
            if not request or not request.FILES.getlist('images'):
                raise serializers.ValidationError({
                    'images': 'At least one image is required.'
                })

        base_price = attrs.get('base_price', getattr(self.instance, 'base_price'))
        discounted_price = attrs.get('discounted_price', getattr(self.instance, 'discounted_price', None))

        if discounted_price and discounted_price >= base_price:
            raise serializers.ValidationError({
                'discounted_price': 'Discounted price cannot be greater than base price.'
            })

        return attrs

    def _get_attribute(self, key: str) -> AttributeModel:
        try:
            attribute = AttributeModel.objects.get(key=key)
        except AttributeModel.DoesNotExist:
            raise serializers.ValidationError({
                'attribute': f'Attribute "{key}" does not exist.'
            })

        return attribute

    def _create_attribute_list(self, product: ProductModel, attribute_list: list):
        for attr_data in attribute_list:
            attribute = self._get_attribute(attr_data['key'])

            for val in attr_data['values']:
                AttributeValueModel.objects.get_or_create(
                    product=product,
                    attribute=attribute,
                    value=val,
                )

    @transaction.atomic
    def create(self, validated_data):
        images = validated_data.pop('images', [])
        attribute_list = validated_data.pop('attribute_list', [])

        product = ProductModel.objects.create(**validated_data)

        for image in images:
            ProductImageModel.objects.create(product=product, image=image)

        self._create_attribute_list(product, attribute_list)

        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        images = validated_data.pop('images', [])
        attribute_list = validated_data.pop('attribute_list', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        for image in images:
            ProductImageModel.objects.create(product=instance, image=image)

        if attribute_list is not None:
            instance.values.all().delete()
            self._create_attribute_list(instance, attribute_list)

        return instance


class AllProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    category = serializers.CharField(source='category.slug')
    category_label = serializers.CharField(source='category.name')
    images = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    attribute_list = serializers.SerializerMethodField()

    class Meta:
        model = ProductModel
        fields = [
            'id',
            'name',
            'category',
            'category_label',
            'description',
            'stock',
            'base_price',
            'discounted_price',
            'images',
            'is_available',
            'attribute_list',
        ]

    def get_images(self, obj) -> list:
        request = self.context.get('request')
        return [
            {
                'url': request.build_absolute_uri(img.image.url) if request else img.image.url,
                'alt': obj.name,
            }
            for img in obj.images.all()
        ]

    def get_is_available(self, obj) -> bool:
        return obj.stock > 0

    def get_attribute_list(self, obj) -> list:
        grouped = {}

        for av in obj.values.select_related('attribute').all():
            key = av.attribute.key

            if key not in grouped:
                grouped[key] = {
                    'key': av.attribute.key,
                    'type': av.attribute.type,
                    'values': [],
                }

            grouped[key]['values'].append(av.value)

        return list(grouped.values())


class ProductPaginationSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = AllProductSerializer(many=True)

class AttrValueSerializer(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.ListField()