from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema,OpenApiParameter
from django.db.models import Q
from permission import IsOwnerorReadonly

from paginator import paginate

from .models import (
    ProductModel,
    ProductImageModel,
    CategoryModel,
    AttributeModel,
    AttributeValueModel,
)
from .serializer import (
    AllProductSerializer,
    ProductSerializer,
    ProductImageSerializer,
    CategorySerializer,
    AttributeSerializer,
)
from .schemas.response import (
    GET_PRODUCTS_RESPONSE,
    GET_PRODUCT_RESPONSE,
    POST_PRODUCT_RESPONSE,
    UPDATE_PRODUCT_RESPONSE,
    DELETE_PRODUCT_RESPONSE,
    GET_PRODUCT_IMAGE_RESPONSE,
    UPDATE_PRODUCT_IMAGE_RESPONSE,
    DELETE_IMAGE_RESPONSE,
    GET_CATEGORIES_RESPONSE,
    GET_CATEGORY_RESPONSE,
    POST_CATEGORY_RESPONSE,
    UPDATE_CATEGORY_RESPONSE,
    DELETE_CATEGORY_RESPONSE,
    GET_ATTRIBUTES_RESPONSE,
)


class ProductView(viewsets.ViewSet):
    permission_classes = [IsOwnerorReadonly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return (ProductModel.objects.select_related('category').prefetch_related('images', 'values__attribute').order_by('-id'))

    @extend_schema(responses=GET_PRODUCTS_RESPONSE,
                   description='**برای فیلتر داینامیک**\n\n - **/?key=value&key=value**\n\n - **/?رنگ=blue&جنس=nakh**',
                   parameters=[
                       OpenApiParameter('search', str, description='**جستجو در نام و توضیحات**'),
                       OpenApiParameter('category', str, description='**فیلتر بر اساس دسته‌بندی**'),
                       OpenApiParameter('page', str, description='**رفتن به شماره صفحه**'),
                       OpenApiParameter('page_size', str, description='**تنظیم کردن سایز صفحه**'),
                       OpenApiParameter('رنگ',str,description='**فیلتر داینامیک(رنگ)**'),
                       OpenApiParameter('جنس',str,description='**فیلتر داینامیک(جنس)**'),
                       OpenApiParameter('min_price', int, description='حداقل قیمت'),
                       OpenApiParameter('max_price', int, description='حداکثر قیمت'),
                   ])
    def list(self, request):
        queryset = self.get_queryset()
        search = request.query_params.get("search")
        category = request.query_params.get("category")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        if search:
            queryset = queryset.filter(Q(name__icontains=search) |Q(description__icontains=search))
        if category:
            queryset = queryset.filter(category__name=category)
        valid_attribute_keys = AttributeModel.objects.values_list('key', flat=True)
        for key in valid_attribute_keys:
            param_value = request.query_params.get(key)
            if param_value:
                queryset = queryset.filter(values__attribute__key=key,values__value__iexact=param_value)
        if min_price:
            queryset = queryset.filter(base_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)
        queryset = queryset.distinct()
        paginator = paginate()
        page = paginator.paginate_queryset(queryset, request)
        serializer = AllProductSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(responses=GET_PRODUCT_RESPONSE)
    def retrieve(self, request, pk=None):
        instance = self.get_queryset().filter(pk=pk).first()

        if not instance:
            raise NotFound('Product Not Found.')

        return Response(
            AllProductSerializer(instance, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=ProductSerializer, responses=POST_PRODUCT_RESPONSE)
    @transaction.atomic
    def create(self, request):
        serializer = ProductSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        return Response(
            AllProductSerializer(product, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=ProductSerializer, responses=UPDATE_PRODUCT_RESPONSE)
    @transaction.atomic
    def partial_update(self, request, pk=None):
        product = self.get_queryset().filter(pk=pk).first()

        if not product:
            raise NotFound('Product Not Found.')

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        return Response(
            AllProductSerializer(product, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(responses=DELETE_PRODUCT_RESPONSE)
    def destroy(self, request, pk=None):
        product = self.get_queryset().filter(pk=pk).first()

        if not product:
            raise NotFound('Product Not Found.')

        product.delete()
        return Response({'message': 'Product was deleted.'}, status=status.HTTP_204_NO_CONTENT)


class ProductImageView(viewsets.ViewSet):
    permission_classes = [IsOwnerorReadonly]
    http_method_names = ['get', 'patch', 'delete']

    def get_queryset(self):
        return ProductImageModel.objects.select_related('product').all()

    @extend_schema(responses=GET_PRODUCT_IMAGE_RESPONSE)
    def retrieve(self, request, pk=None):
        image = self.get_queryset().filter(pk=pk).first()

        if not image:
            raise NotFound('Image Not Found.')

        return Response(
            ProductImageSerializer(image, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=ProductImageSerializer, responses=UPDATE_PRODUCT_IMAGE_RESPONSE)
    def partial_update(self, request, pk=None):
        image = self.get_queryset().filter(pk=pk).first()

        if not image:
            raise NotFound('Image Not Found.')

        serializer = ProductImageSerializer(
            image,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        image = serializer.save()

        return Response(
            ProductImageSerializer(image, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(responses=DELETE_IMAGE_RESPONSE)
    def destroy(self, request, pk=None):
        image = self.get_queryset().filter(pk=pk).first()

        if not image:
            raise NotFound('Image Not Found.')

        image.delete()
        return Response({'message': 'Image was deleted.'}, status=status.HTTP_204_NO_CONTENT)


class CategoryView(viewsets.ViewSet):
    permission_classes = [IsOwnerorReadonly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return CategoryModel.objects.all().order_by('-id')

    @extend_schema(responses=GET_CATEGORIES_RESPONSE)
    def list(self, request):
        paginator = paginate()
        page = paginator.paginate_queryset(self.get_queryset(), request)
        serializer = CategorySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(responses=GET_CATEGORY_RESPONSE)
    def retrieve(self, request, pk=None):
        category = self.get_queryset().filter(pk=pk).first()

        if not category:
            raise NotFound('Category Not Found.')

        return Response(CategorySerializer(category).data, status=status.HTTP_200_OK)

    @extend_schema(request=CategorySerializer, responses=POST_CATEGORY_RESPONSE)
    def create(self, request):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()

        return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=CategorySerializer, responses=UPDATE_CATEGORY_RESPONSE)
    def partial_update(self, request, pk=None):
        category = self.get_queryset().filter(pk=pk).first()

        if not category:
            raise NotFound('Category Not Found.')

        serializer = CategorySerializer(category, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()

        return Response(CategorySerializer(category).data, status=status.HTTP_200_OK)

    @extend_schema(responses=DELETE_CATEGORY_RESPONSE)
    def destroy(self, request, pk=None):
        category = self.get_queryset().filter(pk=pk).first()

        if not category:
            raise NotFound('Category Not Found.')

        category.delete()
        return Response({'message': 'Category was deleted.'}, status=status.HTTP_204_NO_CONTENT)


class AttributeView(viewsets.ViewSet):
    permission_classes = [AllowAny]
    http_method_names = ['get']

    def get_queryset(self):
        return AttributeModel.objects.all().order_by('-id')

    @extend_schema(responses=GET_ATTRIBUTES_RESPONSE)
    def list(self, request):
        attr = self.get_queryset().values_list('key','values__value').distinct()
        data = {}
        for key,values in attr:
            data.setdefault(key,[]).append(values)
        result = [{'key': key, 'values': values} for key, values in data.items()]
        return Response(result, status=status.HTTP_200_OK)

    @extend_schema(responses=GET_ATTRIBUTES_RESPONSE)
    def retrieve(self, request, pk=None):
        attribute = self.get_queryset().filter(pk=pk).first()

        if not attribute:
            raise NotFound('Attribute Not Found.')

        return Response(AttributeSerializer(attribute).data, status=status.HTTP_200_OK)