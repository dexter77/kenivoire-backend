from django.urls import path
from .views import AdListCreateView, AdDetailView

urlpatterns = [
    path('', AdListCreateView.as_view(), name='ad-list-create'),
    path('<int:pk>/', AdDetailView.as_view(), name='ad-detail'),
]
