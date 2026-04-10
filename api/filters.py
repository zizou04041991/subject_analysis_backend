import django_filters
from django.db import models
from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter, DateFilter
from .models import *
from usuarios.models import *

class ContieneFilter(CharFilter):
    """Filtro personalizado que siempre usa 'icontains'"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('lookup_expr', 'icontains')
        super().__init__(*args, **kwargs)


class SemestreFilter(FilterSet):
    """Filtros para Semestre"""
    # Filtros de texto con contains
    numero = ContieneFilter()  # Busca por texto del número (ej: "1er")
    numero_exacto = CharFilter(field_name='numero', lookup_expr='exact')
    numero_min = NumberFilter(field_name='numero', lookup_expr='gte')
    numero_max = NumberFilter(field_name='numero', lookup_expr='lte')
    
    class Meta:
        model = Semestre
        fields = {
            'numero': ['exact', 'icontains', 'gte', 'lte'],
        }


class AsignaturaFilter(FilterSet):
    """Filtros para Asignatura"""
    # Filtros de texto con contains
    nombre = ContieneFilter()
    
    # Filtros de fecha
    fecha_creacion_desde = DateFilter(field_name='fecha_creacion', lookup_expr='gte')
    fecha_creacion_hasta = DateFilter(field_name='fecha_creacion', lookup_expr='lte')
    fecha_actualizacion_desde = DateFilter(field_name='fecha_actualizacion', lookup_expr='gte')
    fecha_actualizacion_hasta = DateFilter(field_name='fecha_actualizacion', lookup_expr='lte')
    
    class Meta:
        model = Asignatura
        fields = {
            'nombre': ['exact', 'icontains', 'startswith'],
        }

'''
class EstudianteFilter(FilterSet):
    """Filtros para Estudiante"""
    # Filtros de texto con contains
    nombre = ContieneFilter()
    apellidos = ContieneFilter()
    curp = ContieneFilter()
    
    # Búsqueda en nombre completo (nombre + apellidos)
    nombre_completo = CharFilter(method='filter_nombre_completo')
    
    # Filtros por semestre
    semestre_actual = NumberFilter(field_name='semestre_actual__numero')
    semestre_actual__numero = ContieneFilter(field_name='semestre_actual__numero')
    
    # Filtros de fecha
    fecha_registro_desde = DateFilter(field_name='fecha_registro', lookup_expr='gte')
    fecha_registro_hasta = DateFilter(field_name='fecha_registro', lookup_expr='lte')
    fecha_actualizacion_desde = DateFilter(field_name='fecha_actualizacion', lookup_expr='gte')
    fecha_actualizacion_hasta = DateFilter(field_name='fecha_actualizacion', lookup_expr='lte')
    
    class Meta:
        model = Estudiante
        fields = {
            'nombre': ['exact', 'icontains', 'startswith'],
            'apellidos': ['exact', 'icontains', 'startswith'],
            'curp': ['exact', 'icontains', 'startswith'],
            'semestre_actual': ['exact'],
        }
    
    def filter_nombre_completo(self, queryset, name, value):
        """Filtro personalizado para buscar en nombre + apellidos"""
        return queryset.filter(
            models.Q(nombre__icontains=value) | 
            models.Q(apellidos__icontains=value)
        )
'''
class ContieneFilter(CharFilter):
    def __init__(self, *args, **kwargs):
        kwargs['lookup_expr'] = 'icontains'
        super().__init__(*args, **kwargs)
