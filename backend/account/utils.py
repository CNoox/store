from django.template.loader import render_to_string
import secrets
import hashlib
from .models import UserTokenModel


def otp_mail(email,code,store_name):
    text_content = render_to_string(
        'emails/otp.html',
        context={
            'store_name': store_name,
            'user_name': email,
            'otp': code
        }
    )
    return text_content

def base_mail(store_name,subject,content ):
    text_content = render_to_string(
        "emails/base.html",
        context={
            'store_name': store_name,
            'subject': subject,
            'content': content
        }
    )
    return text_content


def create_token(user):
    raw_token = secrets.token_urlsafe(32)
    user_token = hashlib.sha256(raw_token.encode()).hexdigest()
    UserTokenModel.objects.create(user=user,token=user_token)
    return raw_token