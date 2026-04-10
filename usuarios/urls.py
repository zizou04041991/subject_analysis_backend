
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'admin', AdminViewSet, basename='admin')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
    # ... otras URLs (login, registro de estudiantes, etc.)
]

