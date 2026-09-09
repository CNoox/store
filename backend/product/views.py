from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from permission import IsOwnerorReadonly
from .serializer import AllProductSerializer,ProductSerializer,ProductImageSerializer,ProductAttributeSerializer,AttributeValueSerializer
from .models import ProductModel,CategoryModel,ProductImageModel,ProductAttributeModel,AttributeValueModel
from paginator import paginate
from rest_framework.exceptions import NotFound,PermissionDenied,ValidationError
from .schemas.response import GET_PRODUCT_RESPONSE,POST_PRODUCT_RESPONSE,DELETE_IMAGE_RESPONSE
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny

import json
# Create your views here.

class ProductView(viewsets.ViewSet):
    permission_classes = [AllowAny]
    queryset = ProductModel.objects.all()
    @extend_schema(
        responses=GET_PRODUCT_RESPONSE
    )
    def list(self, request):
        instance = self.queryset.order_by('-id')
        paginator = paginate()
        page = paginator.paginate_queryset(instance, request)
        serializer = AllProductSerializer(instance=page, many=True)
        return paginator.get_paginated_response(serializer.data)
    @extend_schema(
        description='''.اینجا باید آیدی کالا رو توی کوئری قرار بدی''',
        request=ProductSerializer,
        responses=GET_PRODUCT_RESPONSE
    )
    def retrieve(self, request, pk=None):
        instance = self.queryset.filter(pk=pk).first()
        if not instance:
            raise NotFound
        serializer = AllProductSerializer(instance=instance)
        return Response(data=serializer.data)
    @extend_schema(
        description='''.اینجا باید آیدی کالا رو توی کوئری قرار بدی''',
        responses=POST_PRODUCT_RESPONSE
    )
    def destroy(self, request, pk=None):
        instance = self.queryset.filter(pk=pk).first()
        if not instance:
            raise NotFound
        instance.delete()
        return Response({'message':'Product was delete.'},status=status.HTTP_204_NO_CONTENT)
    @extend_schema(
        description=''': لطفا همه اطلاعات لازم رو ارسال کن. نمونه به صورت فرم دیتا\n
        name: T-Shirtt
        category: clothes
        description: T-Shirt cotton
        stock: 25
        base_price: 500000
        discount_percent: 10
        attribute_list: [{"key":"color","type":"color","is_selective":true,"values":[{"label":"قرمز","value":"red","price_modifier_percent":0},{"label":"آبی","value":"blue","price_modifier_percent":0}]},{"key":"size","type":"text","is_selective":true,"values":[{"label":"کوچک","value":"S","price_modifier_percent":0},{"label":"متوسط","value":"M","price_modifier_percent":0},{"label":"بزرگ","value":"L","price_modifier_percent":0}]}]
        image: تصاویر شما''',
        request=AllProductSerializer,
        responses=POST_PRODUCT_RESPONSE
    )
    def create(self, request):
        data = request.data.dict()
        if 'attribute_list' in data:
            data['attribute_list'] = json.loads(data['attribute_list'])
        product_serializer = ProductSerializer(data=data)
        product_serializer.is_valid(raise_exception=True)
        category_name = product_serializer.validated_data['category']
        category = CategoryModel.objects.filter(name=category_name).first()
        if not category:
            raise NotFound("Category Not Found")
        product_data = product_serializer.validated_data.copy()
        product_attributes = product_data.pop('attributes')
        if not request.FILES.getlist('images'):
            raise ValidationError({'images': 'At least one image is required.'})
        product = ProductModel.objects.create(
            name=product_data['name'],
            category=category,
            description=product_data['description'],
            stock=product_data['stock'],
            base_price=product_data['base_price'],
            discount_percent=product_data['discount_percent']
        )
        for image in request.FILES.getlist('images'):
            ProductImageModel.objects.create(product=product,image=image)
        for attribute_data in product_attributes:
            attribute_values = attribute_data.pop('values')
            attribute = ProductAttributeModel.objects.create(
                product=product,
                key=attribute_data['key'],
                type=attribute_data['type'],
                is_selective=attribute_data['is_selective']
            )
            for value_data in attribute_values:
                AttributeValueModel.objects.create(
                    attribute=attribute,
                    label=value_data['label'],
                    value=value_data['value']
                )
        return Response(AllProductSerializer(instance=product).data, status=status.HTTP_201_CREATED)
    @extend_schema(
        description=''': لطفا یکی از این اطلاعات رو ارسال کن. نمونه به صورت فرم دیتا\n
                name: T-Shirtt
                category: clothes
                description: T-Shirt cotton
                stock: 25
                base_price: 500000
                discount_percent: 10
                attribute_list: [{"key":"color","type":"color","is_selective":true,"values":[{"label":"قرمز","value":"red","price_modifier_percent":0},{"label":"آبی","value":"blue","price_modifier_percent":0}]},{"key":"size","type":"text","is_selective":true,"values":[{"label":"کوچک","value":"S","price_modifier_percent":0},{"label":"متوسط","value":"M","price_modifier_percent":0},{"label":"بزرگ","value":"L","price_modifier_percent":0}]}]
                image: تصاویر شما''',
        request=AllProductSerializer,
        responses=GET_PRODUCT_RESPONSE
    )
    def partial_update(self, request, pk=None):
        product = ProductModel.objects.filter(pk=pk).first()
        if not product:
            raise NotFound("Product Not Found")
        data = request.data.dict()
        if 'attribute_list' in data:
            data['attribute_list'] = json.loads(data['attribute_list'])
        product_serializer = ProductSerializer(product, data=data, partial=True)
        product_serializer.is_valid(raise_exception=True)
        product_data = product_serializer.validated_data.copy()
        if 'category' in product_data:
            category_name = product_data['category']
            category = CategoryModel.objects.filter(name=category_name).first()
            if not category:
                raise NotFound("Category Not Found")
            product.category = category
            product_data.pop('category')
        product_attributes = product_data.pop('attributes', None)
        if 'name' in product_data:
            product.name = product_data['name']
        if 'description' in product_data:
            product.description = product_data['description']
        if 'stock' in product_data:
            product.stock = product_data['stock']
        if 'base_price' in product_data:
            product.base_price = product_data['base_price']
        if 'discount_percent' in product_data:
            product.discount_percent = product_data['discount_percent']
        product.save()
        for image in request.FILES.getlist('images'):
            ProductImageModel.objects.create(product=product, image=image)
        if product_attributes is not None:
            product.attributes.all().delete()
            for attribute_data in product_attributes:
                attribute_values = attribute_data.pop('values')
                attribute = ProductAttributeModel.objects.create(
                    product=product,
                    key=attribute_data['key'],
                    type=attribute_data['type'],
                    is_selective=attribute_data['is_selective']
                )
                for value_data in attribute_values:
                    AttributeValueModel.objects.create(
                        attribute=attribute,
                        label=value_data['label'],
                        value=value_data['value'],
                        price_modifier_percent=value_data['price_modifier_percent']
                    )
        return Response(AllProductSerializer(instance=product).data, status=status.HTTP_200_OK)

class ProductImageView(viewsets.ModelViewSet):
    http_method_names = ['delete','get','patch']
    permission_classes = [AllowAny]
    serializer_class = ProductImageSerializer
    queryset = ProductImageModel.objects.all()
    @extend_schema(
        responses=DELETE_IMAGE_RESPONSE,
    )
    def destroy(self, request, pk=None):
        image = ProductImageModel.objects.filter(pk=pk).first()
        if not image:
            raise NotFound("Image Not Found")
        image.delete()
        return Response({'message': 'Image was deleted.'},status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, pk=None):
        image = ProductImageModel.objects.filter(pk=pk).first()
        if not image:
            raise NotFound("Image Not Found")
        serializer = ProductImageSerializer(image)
        return Response(serializer.data)
    @extend_schema(
        request=ProductImageSerializer,
    )
    def partial_update(self, request, pk=None):
        image = self.queryset.filter(pk=pk).first()
        if not image:
            raise NotFound("Image Not Found")
        receive_image = request.FILES.get('image')
        if not receive_image:
            raise ValidationError({'image': 'At least one image is required.'})
        image.image = receive_image
        image.save()
        return Response(ProductImageSerializer(instance=image).data, status=status.HTTP_200_OK)

