from product.serializer import (
    AllProductSerializer,
    ProductImageSerializer,
    CategorySerializer,
    AttrValueSerializer,
    ProductPaginationSerializer,
)
from account.serializer import SCHErrorResponseSerializer, SCHMessageSerializer

GET_PRODUCTS_RESPONSE = {200: ProductPaginationSerializer}
GET_PRODUCT_RESPONSE = {200: AllProductSerializer, 404: SCHErrorResponseSerializer}
POST_PRODUCT_RESPONSE = {201: AllProductSerializer, 400: SCHErrorResponseSerializer, 404: SCHErrorResponseSerializer}
UPDATE_PRODUCT_RESPONSE = {200: AllProductSerializer, 400: SCHErrorResponseSerializer, 404: SCHErrorResponseSerializer}
DELETE_PRODUCT_RESPONSE = {204: SCHMessageSerializer, 404: SCHErrorResponseSerializer}

GET_PRODUCT_IMAGE_RESPONSE = {200: ProductImageSerializer, 404: SCHErrorResponseSerializer}
UPDATE_PRODUCT_IMAGE_RESPONSE = {200: ProductImageSerializer, 400: SCHErrorResponseSerializer, 404: SCHErrorResponseSerializer}
DELETE_IMAGE_RESPONSE = {204: SCHMessageSerializer, 404: SCHErrorResponseSerializer}

GET_CATEGORIES_RESPONSE = {200: CategorySerializer}
GET_CATEGORY_RESPONSE = {200: CategorySerializer, 404: SCHErrorResponseSerializer}
POST_CATEGORY_RESPONSE = {201: CategorySerializer, 400: SCHErrorResponseSerializer}
UPDATE_CATEGORY_RESPONSE = {200: CategorySerializer, 400: SCHErrorResponseSerializer, 404: SCHErrorResponseSerializer}
DELETE_CATEGORY_RESPONSE = {204: SCHMessageSerializer, 404: SCHErrorResponseSerializer}

GET_ATTRIBUTES_RESPONSE = {200: AttrValueSerializer}