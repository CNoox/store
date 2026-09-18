from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema

from paginator import paginate

from .models import (
    ProductModel,
    ProductImageModel,
    CategoryModel,
    AttributeModel,
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
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return (
            ProductModel.objects
            .select_related('category')
            .prefetch_related('images', 'values__attribute')
            .order_by('-id')
        )

    @extend_schema(responses=GET_PRODUCTS_RESPONSE)
    def list(self, request):
        paginator = paginate()
        page = paginator.paginate_queryset(self.get_queryset(), request)
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
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]
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
        serializer = AttributeSerializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses=GET_ATTRIBUTES_RESPONSE)
    def retrieve(self, request, pk=None):
        attribute = self.get_queryset().filter(pk=pk).first()

        if not attribute:
            raise NotFound('Attribute Not Found.')

        return Response(AttributeSerializer(attribute).data, status=status.HTTP_200_OK)