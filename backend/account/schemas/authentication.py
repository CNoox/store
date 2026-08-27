from drf_spectacular.extensions import OpenApiAuthenticationExtension


class CustomTokenAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'account.authentication.CustomTokenAuthentication'
    name = 'BearerAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'Token',
        }