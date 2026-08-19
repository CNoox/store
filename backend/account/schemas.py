from .serializer import *

LOGIN_OTP_RESPONSES = {
    200: SCHMessageSerializer,
    400: SCHErrorResponseSerializer
}
VERIFY_OTP_RESPONSES = {
    200: SCHMessageSerializer,
    201: SCHMessageSerializer,
    400: SCHErrorResponseSerializer
}
