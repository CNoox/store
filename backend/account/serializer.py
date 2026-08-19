from rest_framework import serializers
from .models import UserModel


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