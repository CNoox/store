from rest_framework import serializers
from .models import UserModel,ProfileModel
import jdatetime
from zoneinfo import ZoneInfo


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

class EmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    def validate_otp(self, otp):
        try:
            otp_2 = int(otp)
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
    first_name = ProfileSerializer(source='profile.first_name',read_only=True)
    last_name = ProfileSerializer(source='profile.last_name',read_only=True)
    avatar = ProfileSerializer(source='profile.avatar.url',read_only=True)
    created_at = serializers.SerializerMethodField(source='created_at',read_only=True)
    last_login = serializers.SerializerMethodField(source='last_login',read_only=True)
    class Meta:
        model = UserModel
        fields = ['id', 'email', 'phone_number',
                  'is_superuser', 'first_name',
                  'last_name', 'avatar',
                  'created_at', 'last_login']

    def get_created_at(self, obj):
        iran_time = obj.created_at.astimezone(ZoneInfo('Asia/Tehran'))
        return jdatetime.datetime.fromgregorian(
            datetime=iran_time
        ).strftime('%Y/%m/%d %H:%M:%S')

    def get_last_login(self, obj):
        iran_time = obj.last_login.astimezone(ZoneInfo('Asia/Tehran'))
        return jdatetime.datetime.fromgregorian(
            datetime=iran_time
        ).strftime('%Y/%m/%d %H:%M:%S')

    def update(self, instance, validated_data):
        is_active = validated_data.get('is_active')
        instance.is_active = is_active
        instance.save()
        return instance

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