from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AdListCreateView, AdDetailView, AdViewSet

router = DefaultRouter()
router.register(r'ads', AdViewSet, basename='ads')

urlpatterns = [
    path('', AdListCreateView.as_view(), name='ad-list-create'),
    path('<int:pk>/', AdDetailView.as_view(), name='ad-detail'),
]
