from django.urls import path
from .views import OrderViewSet

app_name = 'order'

urlpatterns = [
    path('', OrderViewSet.as_view({'get': 'list'}), name='order'),
    path('<str:pk>/', OrderViewSet.as_view({'get': 'retrieve'}), name='order-key'),
]
