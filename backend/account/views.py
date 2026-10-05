import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializer import (EmailSerializer, EmailOTPSerializer,
                         UserSerializer, UserListSerializer,
                         IsactiveSerializer, ProfleUserSerializer, SCHMessageSerializer, SCHErrorResponseSerializer
                         )
from rest_framework import status, viewsets
from .tasks import update_last_login_task
from .models import UserModel, ProfileModel
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .schemas.response import LOGIN_OTP_RESPONSES, VERIFY_OTP_RESPONSES, LOGOUT_RESPONSES
from django.utils import timezone
from datetime import timedelta
from .features.send_otp import send_otp
from account.core.exceptions import Throttled, ValidationError, PermissionDenied
from .utils import create_token
from permission import IsSuperUser
from paginator import paginate
from django.db.models import Q, Value
from django.db.models.functions import Concat
from rest_framework.exceptions import NotFound
from rest_framework.parsers import MultiPartParser, FormParser

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
        if email in ('admin@example.com','ban@example.com') and code == '123456':
            user = UserModel.objects.get(email=email)
            if user.is_active == False:
                raise PermissionDenied('User is banned.')
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
                    ProfileModel.objects.get_or_create(user=user)
                    update_last_login_task.delay(pk=user.pk)
                    token = create_token(user=user)
                    serializer = UserSerializer(instance=user)
                    return Response({'data': {'user': serializer.data}, 'token': token}, status=status.HTTP_200_OK)
                user = UserModel.objects.create_user(email=email)
                ProfileModel.objects.get_or_create(user=user)
                update_last_login_task.delay(pk=user.pk)
                token = create_token(user=user)
                serializer = UserSerializer(instance=user)
                return Response({'data': {'user': serializer.data}, 'token': token}, status=status.HTTP_201_CREATED)
            raise ValidationError('OTP code verification failed.')
        except (TypeError, KeyError) as e:
            raise ValidationError('OTP code verification failed.')

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
    queryset = UserModel.objects.all().order_by('id').select_related('profile')
    @extend_schema(
        parameters=[
            OpenApiParameter('search', str, description='**جستجو در نام و ایمیل و شماره تماس**'),
            OpenApiParameter('page', str, description='**رفتن به شماره صفحه**'),
            OpenApiParameter('page_size', str, description='**تنظیم کردن سایز صفحه**'),
        ],
    )
    def list(self, request):
        search = request.query_params.get('search')
        queryset = self.queryset
        if search:
            queryset = queryset.annotate(
                full_name=Concat(
                    'profile__first_name',
                    Value(' '),
                    'profile__last_name'
                )
            ).filter(
                Q(phone_number__icontains=search) |
                Q(email__icontains=search) |
                Q(profile__first_name__icontains=search) |
                Q(profile__last_name__icontains=search) |
                Q(full_name=search)
            )
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


@extend_schema(tags=['Profile'])
class ProfileView(viewsets.ViewSet):
    http_method_names = ['get', 'patch']
    permission_classes = [IsAuthenticated]
    queryset = UserModel.objects.all().order_by('id').select_related('profile')

    @extend_schema(responses={200: ProfleUserSerializer})
    def list(self, request):
        user_id = request.user.id
        queryset = self.queryset.filter(pk=user_id).first()
        serializer = ProfleUserSerializer(instance=queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=ProfleUserSerializer, responses={200: ProfleUserSerializer})
    def partial_update(self, request):
        user_id = request.user.id
        queryset = self.queryset.filter(pk=user_id).first()
        serializer = ProfleUserSerializer(instance=queryset, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_200_OK)

@extend_schema(tags=['Profile'],description='***برای حذف عکس پروفایل***')
class DeleteAvatarView(APIView):
    http_method_names = ['delete']
    permission_classes = [IsAuthenticated]
    queryset = UserModel.objects.all().order_by('id').select_related('profile')
    @extend_schema(responses={200: SCHMessageSerializer})
    def delete(self, request):
        user_id = request.user.id
        queryset = self.queryset.filter(pk=user_id).first()
        queryset.profile.avatar.delete()
        return Response({'message':'Avatar was deleted.'}, status=status.HTTP_200_OK)