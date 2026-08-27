from rest_framework.exceptions import APIException
from rest_framework import status


class TokenMissing(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication token is required.'
    default_code = 'TOKEN_MISSING'


class TokenExpired(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication token has expired.'
    default_code = 'TOKEN_EXPIRED'

class TokenInvalid(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication token is invalid.'
    default_code = 'TOKEN_INVALID'