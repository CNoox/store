from product.serializer import *
from account.serializer import SCHErrorResponseSerializer,SCHMessageSerializer

GET_PRODUCT_RESPONSE = {
    200:AllProductSerializer
}
POST_PRODUCT_RESPONSE = {
    201: AllProductSerializer,
    400: SCHErrorResponseSerializer,
    401: SCHErrorResponseSerializer,
    403: SCHErrorResponseSerializer,
    404: SCHErrorResponseSerializer,
}
DELETE_IMAGE_RESPONSE = {
    204: SCHMessageSerializer,
    401: SCHErrorResponseSerializer,
    403: SCHErrorResponseSerializer,
    404: SCHErrorResponseSerializer,
}

