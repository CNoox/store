from celery import shared_task

@shared_task
def send_email_task(email,content=None,otp=None,subject=None):
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings
    from .utils import otp_mail,base_mail
    EMAIL_HOST_USER=settings.EMAIL_HOST_USER
    WEBSITE_NAME=settings.WEBSITE_NAME
    if otp:
        html_content=otp_mail(
            email=EMAIL_HOST_USER,
            code=otp,
            store_name=WEBSITE_NAME
        )
        msg=EmailMultiAlternatives(
            subject="OTP code",
            body="Your OTP code is: " + otp,
            from_email=f"{EMAIL_HOST_USER}",
            to=[f"{email}"]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return f'otp code is send. - {otp}'
    html_content=base_mail(
        store_name=WEBSITE_NAME,
        subject=subject,
        content=content,
    )
    msg=EmailMultiAlternatives(
        subject=subject,
        body=content,
        from_email=EMAIL_HOST_USER,
        to=[f"{email}"]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()

@shared_task()
def update_last_login_task(pk):
    from .models import UserModel
    from django.utils import timezone
    user = UserModel.objects.get(pk=pk)
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])