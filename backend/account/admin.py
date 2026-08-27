from django.contrib import admin
from django.contrib.auth.admin import Group
from unfold.admin import ModelAdmin
from .models import UserModel, UserTokenModel
from django_celery_beat.models import (
    PeriodicTask,
    IntervalSchedule,
    CrontabSchedule,
    ClockedSchedule,
    SolarSchedule,
)

# Register your models here.
admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(SolarSchedule)

admin.site.unregister(Group)

@admin.register(UserModel)
class UserModelAdmin(ModelAdmin):
    list_display = ('email','phone_number','is_active','is_staff','is_superuser','created_at','last_login')
    exclude = ('groups','user_permissions','password')
    search_fields = ('email','phone_number')
    list_filter = ('is_staff', 'is_superuser')

@admin.register(UserTokenModel)
class UserTokenModelAdmin(ModelAdmin):
    list_display = ('user','token','created_at','expires_at','is_active')
    search_fields = ('user','token')
