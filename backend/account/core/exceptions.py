from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ValidationError,
    NotFound,
    PermissionDenied,
    AuthenticationFailed,
    Throttled,
    NotAuthenticated,
)
from rest_framework import status
from account.exceptions import TokenMissing, TokenExpired, TokenInvalid

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response
    if isinstance(exc, ValidationError):
        code = "VALIDATION_ERROR"
        message = "The provided data is invalid."
    elif isinstance(exc, NotAuthenticated):
        code = "TOKEN_MISSING"
        message = "Authentication token is required."
    elif isinstance(exc, TokenInvalid):
        code = "TOKEN_INVALID"
        message = "Authentication token is invalid."
    elif isinstance(exc, AuthenticationFailed):
        code = "TOKEN_INVALID"
        message = "Authentication token is invalid."
    elif isinstance(exc, TokenExpired):
        code = "TOKEN_EXPIRED"
        message = "Token has expired."
    elif isinstance(exc, NotFound):
        code = "NOT_FOUND"
        message = "The requested resource was not found."
    elif isinstance(exc, PermissionDenied):
        code = "PERMISSION_DENIED"
        message = "You do not have permission to perform this action."
    elif isinstance(exc, Throttled):
        code = "RATE_LIMIT_EXCEEDED"
        message = "Rate limit exceeded."
    else:
        code = "ERROR"
        message = "An error occurred."
    response.data = {
        "error": {
            "code": code,
            "message": message,
            "details": response.data,
        }
    }
    return response