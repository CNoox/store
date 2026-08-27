from account.serializer import *

LOGIN_OTP_RESPONSES = {
    200: SCHMessageSerializer,
    400: SCHErrorResponseSerializer
}
VERIFY_OTP_RESPONSES = {
    200: SCHMessageSerializer,
    201: SCHMessageSerializer,
    400: SCHErrorResponseSerializer,
    403: SCHErrorResponseSerializer
}
LOGOUT_RESPONSES = {
    200: SCHMessageSerializer,
    401: SCHErrorResponseSerializer
}