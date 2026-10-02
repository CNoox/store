import re

from rest_framework import serializers
from .models import UserModel,ProfileModel
from django.conf import settings


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

class EmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    def validate_otp(self, otp):
        try:
            if len(otp) == 6:
                return otp
            raise serializers.ValidationError('OTP must be 6 digits.')
        except:
            raise serializers.ValidationError('OTP must be digit.')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'email', 'phone_number', 'is_superuser']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileModel
        fields = '__all__'

class UserListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(source='profile.first_name')
    last_name = serializers.CharField(source='profile.last_name')
    avatar = serializers.SerializerMethodField()
    is_active = serializers.BooleanField()
    class Meta:
        model = UserModel
        fields = ['id','first_name',
                  'last_name', 'email',
                  'phone_number', 'avatar',
                  'is_active', 'is_superuser',
                  'created_at', 'last_login',
                  'updated_at'
                  ]

    def get_avatar(self, obj):
        profile = getattr(obj, 'profile', None)

        if not profile or not profile.avatar:
            return None

        return profile.avatar.url
    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance

class IsactiveSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()

class ProfleUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(source='profile.first_name')
    last_name = serializers.CharField(source='profile.last_name')
    email = serializers.EmailField(read_only=True)
    avatar = serializers.ImageField(source='profile.avatar', required=False)
    last_login = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = UserModel
        fields = ['id','first_name',
                  'last_name', 'email',
                  'phone_number', 'avatar',
                  'created_at','last_login',
                  'updated_at'
                  ]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        profile = instance.profile
        profile.first_name = profile_data.get('first_name', profile.first_name)
        profile.last_name = profile_data.get('last_name', profile.last_name)
        profile.avatar = profile_data.get('avatar', profile.avatar)
        instance.save()
        instance.profile.save()
        return instance

    def validate_avatar(self, avatar):
        image = self.initial_data.getlist('avatar')
        if len(image) > 1:
            raise serializers.ValidationError('Only one image can be uploaded.')
        if avatar.size > settings.MAX_IMAGE_SIZE:
            raise serializers.ValidationError(f'Image size must not exceed {settings.MAX_IMAGE_SIZE_COUNT}MB.')

        return avatar

    def validate_phone_number(self, phone_number):
        if re.fullmatch(r'(9\d{9})', phone_number):
            return phone_number
        if re.fullmatch(r'(09\d{9})', phone_number):
            return phone_number[1:]
        raise serializers.ValidationError('Invalid phone number. It must start with `09` and contain 11 digits, or start with `9` and contain 10 digits.')

    def validate_first_name(self, first_name):
        if re.fullmatch(r'^[آ-ی]+$', first_name):
            return first_name
        raise serializers.ValidationError('Invalid first name. It must contain only Persian letters.')

    def validate_last_name(self, last_name):
        if re.fullmatch(r'^[آ-ی]+$', last_name):
            return last_name
        raise serializers.ValidationError('Invalid last name. It must contain only Persian letters.')

#=========================== SCHEMA ===========================

class SCHEmailOTPResponseSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)

class SCHErrorSerializer(serializers.Serializer):
    code = serializers.CharField()
    message = serializers.CharField()
    details = serializers.JSONField()
class SCHErrorResponseSerializer(serializers.Serializer):
    error = SCHErrorSerializer()

class SCHMessageSerializer(serializers.Serializer):
    message = serializers.CharField()