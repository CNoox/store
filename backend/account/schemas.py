from drf_spectacular.utils import OpenApiResponse
from .serializer import *

LOGIN_OTP_RESPONSES = {
    200: OpenApiResponse(description="OTP code is sent."),
    400: OpenApiResponse(description="Invalid credentials"),
}
VERIFY_OTP_RESPONSES = {
    200: OpenApiResponse(EmailOTPResponseSerializer,description="OTP code is sent."),
    201: OpenApiResponse(EmailOTPResponseSerializer,description="OTP code is sent."),
    400: OpenApiResponse(description="Invalid credentials"),
}