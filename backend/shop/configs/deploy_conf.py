DEPLOY = False

MIDDLEWARE_FOR_DEPLOY = []

if DEPLOY == True:
    MIDDLEWARE_FOR_DEPLOY = [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
    ]
    STORAGES = {
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }