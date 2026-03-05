from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError, models
from django_filters.rest_framework import DjangoFilterBackend
from .models import Semestre, Asignatura, Estudiante, Nota
from .serializers import (
    SemestreSerializer, AsignaturaSerializer, 
    EstudianteSerializer, NotaSerializer, PaginacionPersonalizada
)
from .filters import SemestreFilter, AsignaturaFilter, EstudianteFilter, NotaFilter


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


class EstudianteViewSet(viewsets.ModelViewSet):
    queryset = Estudiante.objects.all().select_related('semestre_actual')
    serializer_class = EstudianteSerializer
    pagination_class = PaginacionPersonalizada
    
    # Filtros
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EstudianteFilter
    search_fields = ['nombre', 'apellidos', 'curp']
    ordering_fields = ['id', 'nombre', 'apellidos', 'fecha_registro']
    ordering = ['apellidos', 'nombre']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro adicional para nombre_completo si viene como parámetro directo
        nombre_completo = self.request.query_params.get('nombre_completo')
        if nombre_completo:
            queryset = queryset.filter(
                models.Q(nombre__icontains=nombre_completo) |
                models.Q(apellidos__icontains=nombre_completo)
            )
        
        return queryset
    
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
            
            # Verificar si el estudiante tiene notas registradas
            if instance.notas.exists():
                return Response(
                    {'error': 'No se puede eliminar el estudiante porque tiene notas registradas.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            self.perform_destroy(instance)
            
            return Response(
                {'mensaje': 'Estudiante eliminado correctamente'},
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


class NotaViewSet(viewsets.ModelViewSet):
    queryset = Nota.objects.all().select_related('estudiante', 'asignatura', 'semestre_cursado')
    serializer_class = NotaSerializer
    pagination_class = PaginacionPersonalizada
    
    # Filtros
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = NotaFilter
    search_fields = [
        'estudiante__nombre', 
        'estudiante__apellidos',
        'estudiante__curp',
        'asignatura__nombre',
    ]
    ordering_fields = ['id', 'nota', 'fecha_registro', 'estudiante__nombre', 'asignatura__nombre']
    ordering = ['-fecha_registro']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros adicionales personalizados
        nombre_completo = self.request.query_params.get('estudiante_nombre_completo')
        if nombre_completo:
            queryset = queryset.filter(
                models.Q(estudiante__nombre__icontains=nombre_completo) |
                models.Q(estudiante__apellidos__icontains=nombre_completo)
            )
        
        return queryset
    
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
            self.perform_destroy(instance)
            
            return Response(
                {'mensaje': 'Nota eliminada correctamente'},
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