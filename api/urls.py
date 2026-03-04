from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'semestre', SemestreViewSet)
router.register(r'asignatura', AsignaturaViewSet)
router.register(r'estudiante', EstudianteViewSet)
router.register(r'nota', NotaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]