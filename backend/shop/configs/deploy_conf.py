import os
from dotenv import load_dotenv
load_dotenv()

DEPLOY = os.environ.get('DEPLOY') == 'True'

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