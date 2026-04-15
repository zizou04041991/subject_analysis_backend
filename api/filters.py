import django_filters
from django.db import models
from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter, DateFilter
from .models import *
from usuarios.models import *


# filters.py (en tu app de estudiantes)

from django.contrib.auth import get_user_model
from usuarios.models import Semestre
from django.db import models as django_models

from django.db.models import CharField, Value
from django.db.models.functions import Cast

from django.db.models import CharField, Value
from django.db.models.functions import Concat


User = get_user_model()


class TCPFilter(django_filters.FilterSet):
    # Filtro para número de TCP con coincidencia parcial (contiene)
    numero = django_filters.CharFilter(method='filter_numero_contains', label='Número de TCP (contiene)')

    class Meta:
        model = TCP
        fields = ['numero']

    def filter_numero_contains(self, queryset, name, value):
        # Convierte el número a string y busca si contiene el valor proporcionado
        # Ejemplo: value='1' encontrará TCP con números 1, 10, 11, 21, 101, etc.
        return queryset.annotate(
            numero_str=Cast('numero', output_field=CharField())
        ).filter(numero_str__icontains=value)
    

class StudentFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name = django_filters.CharFilter(field_name='last_name', lookup_expr='icontains')
    curp = django_filters.CharFilter(field_name='curp', lookup_expr='icontains')
    numero_control = django_filters.CharFilter(field_name='numero_control', lookup_expr='icontains')
    semestre_actual = django_filters.ModelChoiceFilter(
        field_name='semestre_actual',
        queryset=Semestre.objects.all(),
        lookup_expr='exact'  # filtro exacto por ID, pero puedes cambiarlo a 'icontains' si usas número
    )
    # Opcional: filtrar por número de semestre (1,2,3...) en lugar de ID
    semestre_numero = django_filters.NumberFilter(
        field_name='semestre_actual__numero',
        lookup_expr='icontains'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'curp', 'numero_control', 'semestre_numero']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo permitir estudiantes
        self.queryset = self.queryset.filter(user_type='student')

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


# filters.py
# filters.py
class NotaFilter(django_filters.FilterSet):
    estudiante_nombre_completo = django_filters.CharFilter(method='filter_nombre_completo')
    asignatura_nombre = django_filters.CharFilter(field_name='asignatura__nombre', lookup_expr='icontains')
    semestre_numero = django_filters.NumberFilter(field_name='semestre__numero')
    tcp_numero = django_filters.NumberFilter(field_name='tcp__numero')
    nota_exacta = django_filters.NumberFilter(field_name='nota')

    def filter_nombre_completo(self, queryset, name, value):
        return queryset.annotate(
            nombre_completo=Concat('estudiante__last_name', Value(' '), 'estudiante__first_name')
        ).filter(nombre_completo__icontains=value)

    class Meta:
        model = Nota
        fields = ['estudiante_nombre_completo', 'asignatura_nombre', 'semestre_numero', 'tcp_numero', 'nota']