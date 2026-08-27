from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed,PermissionDenied
from .models import UserTokenModel
from .exceptions import TokenMissing, TokenExpired, TokenInvalid

import hashlib

from django.utils import timezone


class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        authorization = request.headers.get('Authorization')
        if not authorization:
            return None
        authorization_parts = authorization.split()
        if len(authorization_parts) != 2 or authorization_parts[0].lower() != 'bearer':
            raise AuthenticationFailed('Invalid authorization header.')
        raw_token = authorization_parts[1]
        user_token = hashlib.sha256(raw_token.encode()).hexdigest()
        try:
            token = UserTokenModel.objects.get(token=user_token)
        except UserTokenModel.DoesNotExist:
            raise TokenInvalid('Token is invalid.')
        if not token.is_active:
            raise TokenInvalid('Token is invalid.')
        if token.expires_at is not None and token.expires_at <= timezone.now():
            raise TokenExpired('Token is expired.')
        if not token.user.is_active:
            raise PermissionDenied('User is banned.')
        return (token.user, token)
    def authenticate_header(self, request):
        return 'Bearer'

