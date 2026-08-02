from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class UserModel(AbstractBaseUser, PermissionsMixin):
        id = models.AutoField(primary_key=True)
        email = models.EmailField(max_length=255, unique=True)
        password = models.CharField(max_length=255, blank=True, null=True)
        phone_number = models.CharField(max_length=255, blank=True, null=True)
        created_at = models.DateTimeField(auto_now=True)
        is_active = models.BooleanField(default=True)
        is_staff = models.BooleanField(default=False)
        is_superuser = models.BooleanField(default=False)
        last_login = models.DateTimeField(auto_now_add=True)

        USERNAME_FIELD = 'email'

        REQUIRED_FIELDS = []

        objects = UserManager()

        def __str__(self):
            return self.email
