from .utils_conf import WEBSITE_NAME

SPECTACULAR_SETTINGS = {
    "TITLE": f"{WEBSITE_NAME} API",
    "DESCRIPTION": "API Documentation",
    "VERSION": "1.0.0",
    "COMPONENT_SPLIT_REQUEST": True,
    "SERVE_INCLUDE_SCHEMA": False,
}