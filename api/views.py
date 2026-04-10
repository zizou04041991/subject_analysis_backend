from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError, models
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from usuarios.models import *
from .serializers import (
    SemestreSerializer, AsignaturaSerializer, 
    EstudianteSerializer, NotaSerializer, PaginacionPersonalizada, TCPSerializer
)
from .filters import *
from django.db.models.functions import Concat
from django.db.models import Value, CharField, Q

# views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken



from django.http import JsonResponse
from django.utils import timezone



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny


from django.contrib.auth import get_user_model
from usuarios.serializers import *
from rest_framework import viewsets, permissions

User = get_user_model()

def server_time(request):
    now_local = timezone.localtime()  # hora actual en la zona configurada (America/Matamoros)
    formatted_time = now_local.strftime("%d/%m/%Y %H:%M:%S")
    return JsonResponse({
        "server_time": formatted_time
    })



class SemestreViewSet(viewsets.ModelViewSet):
    queryset = Semestre.objects.all()
    serializer_class = SemestreSerializer
    pagination_class = PaginacionPersonalizada
    
    # Filtros
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SemestreFilter
    search_fields = ['numero']  # Búsqueda general con ?search=
    ordering_fields = ['id', 'numero']
    ordering = ['numero']
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
            
        except ValidationError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except IntegrityError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
            
        except ValidationError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Verificar si hay estudiantes usando este semestre
            if instance.estudiantes_actuales.exists():
                return Response(
                    {'error': 'No se puede eliminar el semestre porque hay estudiantes asignados a él.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            self.perform_destroy(instance)
            
            return Response(
                {'mensaje': 'Semestre eliminado correctamente'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _format_error_response(self, error):
        if hasattr(error, 'detail') and isinstance(error.detail, dict):
            if 'error' in error.detail:
                if isinstance(error.detail['error'], list):
                    return {'error': error.detail['error'][0]}
                return {'error': error.detail['error']}
        
        if isinstance(error, ValidationError):
            if hasattr(error, 'detail'):
                if isinstance(error.detail, dict):
                    for field, errors in error.detail.items():
                        if errors:
                            if isinstance(errors, list):
                                return {'error': str(errors[0])}
                            return {'error': str(errors)}
                elif isinstance(error.detail, list):
                    return {'error': str(error.detail[0]) if error.detail else 'Error de validación'}
                elif isinstance(error.detail, str):
                    return {'error': error.detail}
        
        if isinstance(error, IntegrityError):
            error_str = str(error).lower()
            if "unique constraint" in error_str:
                return {'error': 'Ya existe un registro con estos datos'}
            return {'error': 'Error de integridad en la base de datos'}
        
        return {'error': str(error)}


class AsignaturaViewSet(viewsets.ModelViewSet):
    queryset = Asignatura.objects.all()
    serializer_class = AsignaturaSerializer
    pagination_class = PaginacionPersonalizada
    
    # Filtros
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AsignaturaFilter
    search_fields = ['nombre']
    ordering_fields = ['id', 'nombre', 'fecha_creacion']
    ordering = ['nombre']
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
            
        except ValidationError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except IntegrityError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
            
        except ValidationError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except IntegrityError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Verificar si la asignatura tiene alguna relación (ejemplo con notas)
            # if instance.notas.exists():
            #     return Response(
            #         {'error': 'No se puede eliminar la asignatura porque tiene notas asociadas.'},
            #         status=status.HTTP_400_BAD_REQUEST
            #     )
            
            self.perform_destroy(instance)
            
            return Response(
                {'mensaje': 'Asignatura eliminada correctamente'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _format_error_response(self, error):
        """
        Formatea los errores para dar mensajes más específicos
        """
        if hasattr(error, 'detail'):
            # Si el error ya tiene el formato que queremos (con 'error')
            if isinstance(error.detail, dict) and 'error' in error.detail:
                if isinstance(error.detail['error'], list):
                    return {'error': error.detail['error'][0]}
                return {'error': error.detail['error']}
            
            # Si es un diccionario de errores por campo
            if isinstance(error.detail, dict):
                # Verificar si es el error específico de nombre
                if 'nombre' in error.detail:
                    nombre_errors = error.detail['nombre']
                    if isinstance(nombre_errors, list):
                        return {'error': nombre_errors[0]}
                    return {'error': str(nombre_errors)}
                
                # Verificar si es el error específico de color
                if 'color' in error.detail:
                    color_errors = error.detail['color']
                    if isinstance(color_errors, list):
                        return {'error': color_errors[0]}
                    return {'error': str(color_errors)}
                
                # Para otros campos, devolver el primer error encontrado
                for field, errors in error.detail.items():
                    if errors:
                        if isinstance(errors, list):
                            return {'error': f"{field}: {errors[0]}"}
                        return {'error': f"{field}: {str(errors)}"}
            
            # Si es una lista de errores
            elif isinstance(error.detail, list):
                return {'error': str(error.detail[0]) if error.detail else 'Error de validación'}
            
            # Si es un string
            elif isinstance(error.detail, str):
                return {'error': error.detail}
        
        # Si es IntegrityError
        if isinstance(error, IntegrityError):
            error_str = str(error).lower()
            if "unique constraint" in error_str or "duplicate key" in error_str:
                if "nombre" in error_str:
                    return {'error': 'Ya existe una asignatura con ese nombre.'}
                return {'error': 'Ya existe un registro con estos datos'}
            return {'error': 'Error de integridad en la base de datos'}
        
        # Por defecto
        return {'error': str(error)}


# views.py (parte de EstudianteViewSet)

    # Los métodos update y partial_update ya están heredados

# 3. ViewSet para Estudiantes (user_type='student')
class EstudianteViewSet(viewsets.ModelViewSet):
    """
    CRUD completo para usuarios tipo Estudiante.
    Solo accesible para administradores.
    """
    queryset = User.objects.filter(user_type='student')
    serializer_class = EstudianteSerializer
    #permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(user_type='student')

class TCPViewSet(viewsets.ModelViewSet):
    """ViewSet para TCP"""
    queryset = TCP.objects.all()
    serializer_class = TCPSerializer
    pagination_class = PaginacionPersonalizada
    
    # Filtros
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_class = TCPFilter  # Si tienes un filtro personalizado
    search_fields = ['numero']
    ordering_fields = ['id', 'numero', 'fecha_creacion']
    ordering = ['numero']
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
            
        except ValidationError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except IntegrityError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
            
        except ValidationError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except IntegrityError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Aquí puedes agregar validaciones adicionales antes de eliminar
            # Por ejemplo, verificar si hay asignaturas usando este TCP
            
            self.perform_destroy(instance)
            
            return Response(
                {'error': 'TCP eliminado correctamente'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _format_error_response(self, error):
        """
        Formatear errores para que siempre tengan la estructura {'error': 'mensaje'}
        """
        if hasattr(error, 'detail') and isinstance(error.detail, dict):
            # Si ya tiene el formato {'error': 'mensaje'}
            if 'error' in error.detail:
                if isinstance(error.detail['error'], list):
                    return {'error': error.detail['error'][0]}
                return {'error': error.detail['error']}
            
            # Si viene con formato {'numero': ['mensaje']}
            for field, errors in error.detail.items():
                if errors:
                    if isinstance(errors, list):
                        return {'error': str(errors[0])}
                    return {'error': str(errors)}
        
        # Si es ValidationError con detail como lista o string
        if isinstance(error, ValidationError):
            if hasattr(error, 'detail'):
                if isinstance(error.detail, dict):
                    for field, errors in error.detail.items():
                        if errors:
                            if isinstance(errors, list):
                                return {'error': str(errors[0])}
                            return {'error': str(errors)}
                elif isinstance(error.detail, list):
                    return {'error': str(error.detail[0]) if error.detail else 'Error de validación'}
                elif isinstance(error.detail, str):
                    return {'error': error.detail}
        
        # Si es IntegrityError
        if isinstance(error, IntegrityError):
            error_str = str(error).lower()
            if "unique constraint" in error_str or "duplicate key" in error_str:
                return {'error': 'ya existe este tcp'}
            return {'error': 'Error de integridad en la base de datos'}
        
        # Por defecto
        return {'error': str(error)}

class NotaViewSet(viewsets.ModelViewSet):
    """
    CRUD completo para Notas.
    - GET /notas/ -> lista todas
    - POST /notas/ -> crea una nueva
    - GET /notas/{id}/ -> detalle
    - PUT / PATCH /notas/{id}/ -> actualiza
    - DELETE /notas/{id}/ -> elimina
    """
    queryset = Nota.objects.all()
    serializer_class = NotaSerializer
    #permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Si el usuario autenticado es estudiante, la nota se asigna a él mismo
        if self.request.user.user_type == 'student':
            serializer.save(estudiante=self.request.user)
        else:
            # Admin puede elegir cualquier estudiante (viene en el request)
            serializer.save()

    def get_queryset(self):
        user = self.request.user
        # Los estudiantes solo ven sus propias notas
        if user.user_type == 'student':
            return Nota.objects.filter(estudiante=user)
        # Admin ve todas las notas
        return super().get_queryset()

class EstudianteViewSet(viewsets.ModelViewSet):
    """
    CRUD completo para usuarios tipo Estudiante.
    Solo accesible para administradores.
    """
    queryset = User.objects.filter(user_type='student')
    serializer_class = EstudianteSerializer
    #permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(user_type='student')