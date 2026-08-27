from celery import shared_task
from django.conf import settings
from .utils import otp_mail, base_mail
import resend
from .models import UserModel
from django.utils import timezone

@shared_task
def send_email_task(email, content=None, otp=None, subject=None):
    WEBSITE_NAME = settings.WEBSITE_NAME
    resend.api_key = settings.RESEND_API_KEY
    if otp:
        EMAIL_DOMAIN_USER = f'no-reply@{settings.EMAIL_DOMAIN}'
        html_content = otp_mail(
            email=EMAIL_DOMAIN_USER,
            code=otp,
            store_name=WEBSITE_NAME
        )
        params = {
            "from": EMAIL_DOMAIN_USER,
            "to": [email],
            "subject": "OTP code",
            "html": html_content,
            "text": "Your OTP code is: " + otp,
        }
        response = resend.Emails.send(params)
        return f"otp code is send. - {otp}"
    EMAIL_DOMAIN_USER = f'support@{settings.EMAIL_DOMAIN}'
    html_content = base_mail(
        store_name=WEBSITE_NAME,
        subject=subject,
        content=content,
    )
    params = {
        "from": EMAIL_DOMAIN_USER,
        "to": [email],
        "subject": subject,
        "html": html_content,
        "text": content,
    }
    response = resend.Emails.send(params)
    return response

@shared_task()
def update_last_login_task(pk):
    user = UserModel.objects.get(pk=pk)
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

@shared_task()
def change_password_task(email,password):
    try:
        email = email[0]
        password = password[0]
        user = UserModel.objects.get(email=email)
        user.set_password(password)
        user.save(update_fields=['password'])
        return f'password changed. - for {email}'
    except UserModel.DoesNotExist:
        return f'user does not exist. - {email}'