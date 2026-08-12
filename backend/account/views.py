from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from rest_framework.permissions import AllowAny
from .serializer import EmailSerializer,EmailOTPSerializer
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from .tasks import update_last_login_task
from .models import UserModel
from drf_spectacular.utils import extend_schema
from .schemas import LOGIN_OTP_RESPONSES, VERIFY_OTP_RESPONSES
from django.utils import timezone
from datetime import timedelta
from .features.send_otp import send_otp

# Create your views here.


class LoginEmailOTPView(APIView):
    """
    Send an OTP code to the specified email address.

    Responses:
        200: OTP code sent successfully.
        400: Invalid email.
    """
    http_method_names = ['post']
    permission_classes = [AllowAny]
    @extend_schema(
        request=EmailSerializer,
        responses=LOGIN_OTP_RESPONSES,
    )
    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        info = cache.get(email)
        if info is None:
            send_otp(email)
            return Response({'message': 'OTP code is send.'}, status=status.HTTP_200_OK)
        send_time = info['send_otp_date']
        if timezone.now() > send_time + timedelta(seconds=60):
            send_otp(email)
            return Response({'message': 'OTP code is send.'}, status=status.HTTP_200_OK)
        left = send_time + timedelta(seconds=60) - timezone.now()
        left_type = type(left)
        return Response({'message': 'OTP is already send', 'left_time': left.seconds}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class VerifyOTPView(APIView):
    """
    Verify an OTP code and return an authentication token.

    Returns:
        200: OTP verified successfully.
        201: New user created and authenticated.
        400: Invalid email or OTP.
    """
    http_method_names = ['post']
    permission_classes = [AllowAny]
    @extend_schema(
        request=EmailOTPSerializer,
        responses=VERIFY_OTP_RESPONSES,
    )
    def post(self, request):
        serializer = EmailOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['otp']
        info = cache.get(email)
        try:
            code_2 = info['code']
            flag = info['flag']
            if code == code_2:
                cache.delete(email)
                if flag == 1:
                    user = UserModel.objects.get(email=email)
                    update_last_login_task.delay(pk=user.pk)
                    token = str(AccessToken.for_user(user))
                    return Response({'message':'Welcome back.', 'token':token}, status=status.HTTP_200_OK)
                user = UserModel.objects.create_user(email=email)
                update_last_login_task.delay(pk=user.pk)
                token = str(AccessToken.for_user(user))
                return Response({'message': 'Account created.', 'token': token}, status=status.HTTP_201_CREATED)
            return Response({'message':'OTP code is invalid.'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message':'OTP code is invalid.'}, status=status.HTTP_400_BAD_REQUEST)

