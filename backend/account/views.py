from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializer import EmailSerializer,EmailOTPSerializer,UserSerializer,UserListSerializer,IsactiveSerializer
from rest_framework import status, viewsets
from .tasks import update_last_login_task
from .models import UserModel
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .schemas.response import LOGIN_OTP_RESPONSES, VERIFY_OTP_RESPONSES, LOGOUT_RESPONSES
from django.utils import timezone
from datetime import timedelta
from .features.send_otp import send_otp
from account.core.exceptions import Throttled, ValidationError, PermissionDenied
from .utils import create_token
from permission import IsSuperUser
from paginator import paginate
from django.db.models import Q
from rest_framework.exceptions import NotFound

# Create your views here.


class LoginEmailOTPView(APIView):
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
        # DEMO
        if email == 'admin@example.com':
            return Response({'message': 'OTP code is send.'}, status=status.HTTP_200_OK)
        info = cache.get(email)
        if info is None:
            send_otp(email)
            return Response({'message': 'OTP code is send.'}, status=status.HTTP_200_OK)
        send_time = info['send_otp_date']
        if timezone.now() > send_time + timedelta(seconds=60):
            send_otp(email)
            return Response({'message': 'OTP code is send.'}, status=status.HTTP_200_OK)
        left = send_time + timedelta(seconds=60) - timezone.now()
        raise Throttled(left.seconds)




class VerifyOTPView(APIView):
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
        # DEMO
        if email == 'admin@example.com' and code == '123456':
            user = UserModel.objects.get(email=email)
            token = create_token(user=user)
            serializer = UserSerializer(instance=user)
            return Response({'data': {'user': serializer.data}, 'token': token}, status=status.HTTP_200_OK)
        info = cache.get(email)
        try:
            code_2 = info['code']
            flag = info['flag']
            if code == code_2:
                cache.delete(email)
                if flag == 1:
                    user = UserModel.objects.get(email=email)
                    if user.is_active == False:
                        raise PermissionDenied('User is banned.')
                    update_last_login_task.delay(pk=user.pk)
                    token = create_token(user=user)
                    serializer = UserSerializer(instance=user)
                    return Response({'data': {'user': serializer.data}, 'token': token}, status=status.HTTP_200_OK)
                user = UserModel.objects.create_user(email=email)
                update_last_login_task.delay(pk=user.pk)
                token = create_token(user=user)
                serializer = UserSerializer(instance=user)
                return Response({'data': {'user': serializer.data}, 'token': token}, status=status.HTTP_201_CREATED)
            raise ValidationError('OTP code verification failed.')
        except (TypeError, KeyError) as e:
            raise ValidationError(f'{e}')

class LogoutView(APIView):
    http_method_names = ['post']
    permission_classes = [IsAuthenticated]
    @extend_schema(
        responses=LOGOUT_RESPONSES
    )
    def post(self, request):
        request.auth.is_active = False
        request.auth.save(update_fields=['is_active'])
        return Response({'message': 'User logged out.'}, status=status.HTTP_200_OK)


class UserListView(viewsets.ViewSet):
    permission_classes = [IsSuperUser]
    http_method_names = ['get', 'patch']
    queryset = UserModel.objects.all().order_by('id')
    @extend_schema(
        parameters=[
            OpenApiParameter('search', str, description='**جستجو در نام و ایمیل و شماره تماس**'),
        ],
    )
    def list(self, request):
        search = request.query_params.get('search')
        queryset = self.queryset
        if search:
            queryset = queryset.filter(Q(phone_number__icontains=search) | Q(email__icontains=search) | Q(profile__first_name__icontains=search) | Q(profile__last_name__icontains=search))
        paginator = paginate()
        page = paginator.paginate_queryset(queryset, request)
        serializer = UserListSerializer(instance=page, many=True)
        return paginator.get_paginated_response(serializer.data)
    @extend_schema(
        request=IsactiveSerializer,description='**نکته! نمیشه ادمین سایت یه ادمین دیگه یا خودشو بن کنه**'
    )
    def partial_update(self, request, pk=None):
        if request.user.id == pk:
            raise PermissionDenied('You can\'t edit yourself.')
        queryset = self.queryset.filter(pk=pk).first()
        if queryset.is_superuser == True:
            raise PermissionDenied('You can\'t edit superuser members.')
        if not queryset:
            raise NotFound('User not found.')
        serializer = UserListSerializer(instance=queryset,data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_200_OK)