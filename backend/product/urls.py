from django.urls import path
from .views import ProductView, ProductImageView, CategoryView, AttributeView

app_name = 'product'
urlpatterns = [
    path('', ProductView.as_view({'get': 'list','post': 'create'}), name='test'),
    path('<int:pk>/', ProductView.as_view({'patch': 'partial_update','get': 'retrieve','delete': 'destroy'})),
    path('image/<int:pk>/', ProductImageView.as_view({'delete': 'destroy','get': 'retrieve','patch':'partial_update'})),
    path('category/', CategoryView.as_view({'get': 'list','post': 'create'})),
    path('category/<int:pk>/', CategoryView.as_view({'delete': 'destroy','get': 'retrieve','patch':'partial_update'})),
    path('types/', AttributeView.as_view({'get': 'list'})),
]