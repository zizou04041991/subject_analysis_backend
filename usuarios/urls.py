
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'admin', AdminViewSet, basename='admin')

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     path('login/change-password/', ChangePasswordView.as_view(), name='change_password'),
     path('login/reset-password/<int:pk>/', ResetPasswordView.as_view(), name='reset-password'),
    path('', include(router.urls)),
    # ... otras URLs (login, registro de estudiantes, etc.)
]

