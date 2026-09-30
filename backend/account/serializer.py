from rest_framework import serializers
from .models import UserModel,ProfileModel


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
    first_name = serializers.CharField(source='profile.first_name',read_only=True)
    last_name = serializers.CharField(source='profile.last_name',read_only=True)
    avatar = serializers.SerializerMethodField(source='profile.avatar.url',read_only=True)
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