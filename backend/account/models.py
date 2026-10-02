from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        if password:
            user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user
    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)
    def create_superuser(self, email, password):
        return self._create_user(email, password, is_staff=True, is_superuser=True)

class UserModel(AbstractBaseUser, PermissionsMixin):
        id = models.AutoField(primary_key=True)
        email = models.EmailField(max_length=255, unique=True)
        password = models.CharField(max_length=255, blank=True, null=True)
        phone_number = models.CharField(max_length=11, blank=True, null=True, unique=True)
        is_active = models.BooleanField(default=True)
        is_staff = models.BooleanField(default=False)
        is_superuser = models.BooleanField(default=False)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        USERNAME_FIELD = 'email'

        REQUIRED_FIELDS = []

        objects = UserManager()

        def __str__(self):
            return self.email


class UserTokenModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

def profile_image_upload_to(instance, filename):
    return f'profile/{instance.user.id}/{filename}'
class ProfileModel(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to=profile_image_upload_to,null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'