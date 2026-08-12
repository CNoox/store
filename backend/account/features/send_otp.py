from account.models import UserModel
from django.utils import timezone
from django.core.cache import cache
import random
from account.tasks import send_email_task
from django.conf import settings

def send_otp(email):
    flag = 0
    send_otp_date = timezone.now()
    if UserModel.objects.filter(email=email).exists():
        flag = 1
    code = str(random.randint(0, 999999)).zfill(6)
    cache.set(email, {'code': code, 'flag': flag, 'send_otp_date': send_otp_date}, timeout=settings.CACHE_TTL)
    send_email_task.delay(email=email, otp=code)
    return