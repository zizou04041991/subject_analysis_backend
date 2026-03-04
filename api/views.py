from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from .models import *
from .serializers import *

# pagination.py (nuevo archivo)

from rest_framework.pagination import PageNumberPagination


class PaginacionPersonalizada(PageNumberPagination):
    page_size = 10  # Elementos por página
    page_size_query_param = 'page_size'  # Permitir al cliente cambiar el tamaño
    max_page_size = 100  # Tamaño máximo permitido
    page_query_param = 'page'  # Nombre del parámetro para la página
    
    def get_paginated_response(self, data):
        return Response({
            'total': self.page.paginator.count,
            'page': self.page.number,
            'page_size': self.page.paginator.per_page,
            'total_pages': self.page.paginator.num_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

class NotaViewSet(viewsets.ModelViewSet):
    queryset = Nota.objects.all().select_related('estudiante', 'asignatura', 'semestre_cursado')
    serializer_class = NotaSerializer
    pagination_class = PaginacionPersonalizada  # <-- Agregar esta línea
    
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
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
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
    pagination_class = PaginacionPersonalizada  # <-- Agregar esta línea



class SemestreViewSet(viewsets.ModelViewSet):
    queryset = Semestre.objects.all()
    serializer_class = SemestreSerializer
    pagination_class = PaginacionPersonalizada  # <-- Agregar esta línea
    
    def create(self, request, *args, **kwargs):
        """
        Crear semestre: en éxito devuelve solo los datos, en error devuelve objeto con campo 'error'
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            # ÉXITO: Solo devolver los datos del serializer
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
            
        except ValidationError as e:
            # ERROR: Devolver solo el campo error como string
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except IntegrityError as e:
            # ERROR: Devolver solo el campo error como string
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Actualizar semestre: en éxito devuelve solo los datos, en error devuelve objeto con campo 'error'
        """
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            # ÉXITO: Solo devolver los datos del serializer
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
            
        except ValidationError as e:
            # ERROR: Devolver solo el campo error como string
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Eliminar semestre: en éxito devuelve mensaje simple, en error devuelve objeto con campo 'error'
        """
        try:
            instance = self.get_object()
            
            # Verificar si hay estudiantes usando este semestre
            if instance.estudiantes_actuales.exists():
                return Response(
                    {'error': 'No se puede eliminar el semestre porque hay estudiantes asignados a él.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            self.perform_destroy(instance)
            
            # ÉXITO: Mensaje simple de confirmación
            return Response(
                {'mensaje': 'Semestre eliminado correctamente'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            # ERROR: Devolver solo el campo error como string
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def list(self, request, *args, **kwargs):
        """
        Listar semestres: siempre devuelve los datos sin estructura adicional
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Obtener un semestre específico: devuelve solo los datos
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def _format_error_response(self, error):
        """
        Formatea los errores para devolver solo el campo 'error' como string
        """
        # Si el error ya tiene la estructura personalizada del serializer con 'error' como string
        if hasattr(error, 'detail') and isinstance(error.detail, dict):
            if 'error' in error.detail:
                # Si error.detail['error'] es una lista, tomar el primer elemento
                if isinstance(error.detail['error'], list):
                    return {'error': error.detail['error'][0]}
                # Si ya es string, devolverlo directamente
                return {'error': error.detail['error']}
        
        # Si es un ValidationError de DRF con estructura de lista
        if isinstance(error, ValidationError):
            if hasattr(error, 'detail'):
                # Si es un diccionario con campos
                if isinstance(error.detail, dict):
                    for field, errors in error.detail.items():
                        if errors:
                            # Si errors es una lista, tomar el primer elemento
                            if isinstance(errors, list):
                                return {'error': str(errors[0])}
                            return {'error': str(errors)}
                # Si es una lista directamente
                elif isinstance(error.detail, list):
                    return {'error': str(error.detail[0]) if error.detail else 'Error de validación'}
                # Si es un string
                elif isinstance(error.detail, str):
                    return {'error': error.detail}
        
        # Si es un IntegrityError
        if isinstance(error, IntegrityError):
            error_str = str(error).lower()
            if "unique constraint" in error_str:
                return {'error': 'Ya existe un registro con estos datos'}
            return {'error': 'Error de integridad en la base de datos'}
        
        # Error genérico
        return {'error': str(error)}




class EstudianteViewSet(viewsets.ModelViewSet):
    queryset = Estudiante.objects.all().select_related('semestre_actual')
    serializer_class = EstudianteSerializer
    pagination_class = PaginacionPersonalizada  # <-- Agregar esta línea
    
    def create(self, request, *args, **kwargs):
        """
        Crear estudiante: en éxito devuelve solo los datos, en error devuelve objeto con campo 'error'
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            # ÉXITO: Solo devolver los datos del serializer
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
            
        except ValidationError as e:
            # ERROR: Devolver solo el campo error como string
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except IntegrityError as e:
            # ERROR: Devolver solo el campo error como string
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Actualizar estudiante: en éxito devuelve solo los datos, en error devuelve objeto con campo 'error'
        """
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            # ÉXITO: Solo devolver los datos del serializer
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
            
        except ValidationError as e:
            # ERROR: Devolver solo el campo error como string
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Eliminar estudiante: en éxito devuelve mensaje simple, en error devuelve objeto con campo 'error'
        """
        try:
            instance = self.get_object()
            
            # Verificar si el estudiante tiene notas registradas
            if instance.notas.exists():
                return Response(
                    {'error': 'No se puede eliminar el estudiante porque tiene notas registradas.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            self.perform_destroy(instance)
            
            # ÉXITO: Mensaje simple de confirmación
            return Response(
                {'mensaje': 'Estudiante eliminado correctamente'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            # ERROR: Devolver solo el campo error como string
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def list(self, request, *args, **kwargs):
        """
        Listar estudiantes: siempre devuelve los datos sin estructura adicional
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Obtener un estudiante específico: devuelve solo los datos
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def _format_error_response(self, error):
        """
        Formatea los errores para devolver solo el campo 'error' como string
        """
        # Si el error ya tiene la estructura personalizada del serializer con 'error' como string
        if hasattr(error, 'detail') and isinstance(error.detail, dict):
            if 'error' in error.detail:
                # Si error.detail['error'] es una lista, tomar el primer elemento
                if isinstance(error.detail['error'], list):
                    return {'error': error.detail['error'][0]}
                # Si ya es string, devolverlo directamente
                return {'error': error.detail['error']}
        
        # Si es un ValidationError de DRF con estructura de lista
        if isinstance(error, ValidationError):
            if hasattr(error, 'detail'):
                # Si es un diccionario con campos
                if isinstance(error.detail, dict):
                    for field, errors in error.detail.items():
                        if errors:
                            # Si errors es una lista, tomar el primer elemento
                            if isinstance(errors, list):
                                return {'error': str(errors[0])}
                            return {'error': str(errors)}
                # Si es una lista directamente
                elif isinstance(error.detail, list):
                    return {'error': str(error.detail[0]) if error.detail else 'Error de validación'}
                # Si es un string
                elif isinstance(error.detail, str):
                    return {'error': error.detail}
        
        # Si es un IntegrityError
        if isinstance(error, IntegrityError):
            error_str = str(error).lower()
            if "unique constraint" in error_str:
                return {'error': 'Ya existe un registro con estos datos'}
            return {'error': 'Error de integridad en la base de datos'}
        
        # Error genérico
        return {'error': str(error)}

