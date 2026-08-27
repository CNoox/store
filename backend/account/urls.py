from django.urls import path
from .views import LoginEmailOTPView, VerifyOTPView, LogoutView

app_name = 'account'

urlpatterns = [
    path('login/', LoginEmailOTPView.as_view(), name='login'),
    path('otp/', VerifyOTPView.as_view(), name='otp'),
    path('logout/',LogoutView.as_view(), name='logout'),
]