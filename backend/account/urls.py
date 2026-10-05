from django.urls import path
from .views import (LoginEmailOTPView, VerifyOTPView,
                    LogoutView, UserListView,
                    ProfileView,
                    DeleteAvatarView
                    )

app_name = 'account'

urlpatterns = [
    path('login/', LoginEmailOTPView.as_view(), name='login'),
    path('otp/', VerifyOTPView.as_view(), name='otp'),
    path('logout/',LogoutView.as_view(), name='logout'),
    path('users/', UserListView.as_view({'get':'list'}), name='show-user-list'),
    path('users/<int:pk>/', UserListView.as_view({'patch':'partial_update'}), name='update-user-list'),
    path('profile/', ProfileView.as_view({'get':'list','patch':'partial_update'}), name='profile'),
    path('profile/avatar/', DeleteAvatarView.as_view(), name='delete-avatar'),
]