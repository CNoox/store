import json

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from drf_spectacular.utils import extend_schema
from paginator import paginate
from .models import ProductModel, CategoryModel, ProductImageModel, AttributeModel, ProductVariantModel, VariantAttributeValueModel, StaticAttributeModel
from .serializer import AllProductSerializer, ProductSerializer, ProductImageSerializer
from .schemas.response import *
from .models import CategoryModel
from .serializer import CategorySerializer
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import AttributeModel
from .serializer import AttributeSerializer


class ProductView(viewsets.ViewSet):
    permission_classes = [AllowAny]
    queryset = ProductModel.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    @extend_schema(responses=GET_PRODUCTS_RESPONSE)
    def list(self, request):
        instance = self.queryset.select_related('category').prefetch_related('images', 'variants__variant_attributes__attribute', 'static_attributes__attribute').order_by('-id')
        paginator = paginate()
        page = paginator.paginate_queryset(instance, request)
        serializer = AllProductSerializer(instance=page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(responses=GET_PRODUCT_RESPONSE)
    def retrieve(self, request, pk=None):
        instance = self.queryset.select_related('category').prefetch_related('images', 'variants__variant_attributes__attribute', 'static_attributes__attribute').filter(pk=pk).first()

        if not instance:
            raise NotFound('Product Not Found.')

        serializer = AllProductSerializer(instance=instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ProductSerializer,
        responses=POST_PRODUCT_RESPONSE
    )
    @transaction.atomic
    def create(self, request):
        serializer = ProductSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(AllProductSerializer(product).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=ProductSerializer,
        responses=UPDATE_PRODUCT_RESPONSE
    )
    @transaction.atomic
    def partial_update(self, request, pk=None):
        product = self.queryset.filter(pk=pk).first()

        if not product:
            raise NotFound('Product Not Found.')

        serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(AllProductSerializer(product).data, status=status.HTTP_200_OK)

    @extend_schema(responses=DELETE_PRODUCT_RESPONSE)
    def destroy(self, request, pk=None):
        product = self.queryset.filter(pk=pk).first()

        if not product:
            raise NotFound('Product Not Found.')

        product.delete()
        return Response({'message': 'Product was deleted.'}, status=status.HTTP_204_NO_CONTENT)

class ProductImageView(viewsets.ModelViewSet):
    http_method_names = ['delete', 'get', 'patch']
    permission_classes = [AllowAny]
    serializer_class = ProductImageSerializer
    queryset = ProductImageModel.objects.all()

    @extend_schema(responses=DELETE_IMAGE_RESPONSE)
    def destroy(self, request, pk=None):
        image = self.queryset.filter(pk=pk).first()

        if not image:
            raise NotFound('Image Not Found.')

        image.delete()
        return Response({'message': 'Image was deleted.'}, status=status.HTTP_204_NO_CONTENT)

    @extend_schema(responses=GET_PRODUCT_IMAGE_RESPONSE)
    def retrieve(self, request, pk=None):
        image = self.queryset.filter(pk=pk).first()

        if not image:
            raise NotFound('Image Not Found.')

        return Response(ProductImageSerializer(image).data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ProductImageSerializer,
        responses=UPDATE_PRODUCT_IMAGE_RESPONSE
    )
    def partial_update(self, request, pk=None):
        image = self.queryset.filter(pk=pk).first()

        if not image:
            raise NotFound('Image Not Found.')

        serializer = ProductImageSerializer(image, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        image = serializer.save()
        return Response(ProductImageSerializer(image).data, status=status.HTTP_200_OK)

class CategoryView(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = CategoryModel.objects.all().order_by('-id')
    serializer_class = CategorySerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    @extend_schema(responses=GET_CATEGORIES_RESPONSE)
    def list(self, request):
        paginator = paginate()
        page = paginator.paginate_queryset(self.queryset, request)
        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses=GET_CATEGORY_RESPONSE)
    def retrieve(self, request, pk=None):
        category = self.get_queryset().filter(pk=pk).first()

        if not category:
            raise NotFound('Category Not Found.')

        return Response(self.get_serializer(category).data, status=status.HTTP_200_OK)

    @extend_schema(
        request=CategorySerializer,
        responses=POST_CATEGORY_RESPONSE
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        return Response(self.get_serializer(category).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=CategorySerializer,
        responses=UPDATE_CATEGORY_RESPONSE
    )
    def partial_update(self, request, pk=None):
        category = self.get_queryset().filter(pk=pk).first()

        if not category:
            raise NotFound('Category Not Found.')

        serializer = self.get_serializer(category, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        return Response(self.get_serializer(category).data, status=status.HTTP_200_OK)

    @extend_schema(responses=DELETE_CATEGORY_RESPONSE)
    def destroy(self, request, pk=None):
        category = self.get_queryset().filter(pk=pk).first()

        if not category:
            raise NotFound('Category Not Found.')

        category.delete()
        return Response({'message': 'Category was deleted.'}, status=status.HTTP_204_NO_CONTENT)

class AttributeView(viewsets.ViewSet):
    permission_classes = [AllowAny]
    queryset = AttributeModel.objects.all().order_by('-id')
    http_method_names = ['get']

    @extend_schema(responses=GET_ATTRIBUTES_RESPONSE)
    def list(self, request):
        serializer = AttributeSerializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)