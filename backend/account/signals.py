from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserTokenModel

from datetime import timedelta

from django.conf import settings

@receiver(post_save, sender=UserTokenModel)
def create_userToken(sender, instance, created=False, **kwargs):
    if created:
        created_at = instance.created_at
        expires_at = instance.created_at + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        instance.expires_at = expires_at
        instance.save()
