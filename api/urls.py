from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'semestre', SemestreViewSet)
router.register(r'tcp', TCPViewSet)
router.register(r'asignatura', AsignaturaViewSet)
router.register(r'estudiante', EstudianteViewSet)
router.register(r'nota', NotaViewSet)



urlpatterns = [
    # API endpoints (ej: /api/semestre/, /api/estudiante/, etc)
    path('', include(router.urls)),
    path('server-time/', server_time, name='server_time'),
    
    # Auth endpoints (ej: /api/auth/login/, /api/auth/registro/, etc)
    #path('auth/', include(auth_patterns)),
]