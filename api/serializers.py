from rest_framework import serializers
from .models import *
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

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

class AsignaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asignatura
        fields = '__all__'



# Serializers

class SemestreSerializer(serializers.ModelSerializer):
    """Serializer para Semestre con el valor display del número"""
    # Campo de solo lectura para mostrar el nombre del semestre
    nombre_display = serializers.CharField(source='get_numero_display', read_only=True)
    
    class Meta:
        model = Semestre
        fields = ['id', 'numero', 'nombre_display']
        extra_kwargs = {
            'numero': {
                'validators': [],  # Eliminar validadores automáticos
                'error_messages': {
                    'unique': 'Ya existe un semestre con ese número.',
                }
            }
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar el validador UniqueValidator para numero
        if hasattr(self, 'fields'):
            numero_field = self.fields.get('numero')
            if numero_field:
                numero_field.validators = [
                    v for v in numero_field.validators 
                    if not (hasattr(v, 'code') and v.code == 'unique')
                ]
    
    def validate_numero(self, value):
        """
        Validación personalizada para el número de semestre
        """
        # Verificar si ya existe un semestre con este número (validación manual)
        if not self.instance:  # Para creación
            if Semestre.objects.filter(numero=value).exists():
                raise serializers.ValidationError(
                    f'Ya existe un semestre con el número {value}.'
                )
        else:  # Para actualización
            if value != self.instance.numero:
                if Semestre.objects.filter(numero=value).exists():
                    raise serializers.ValidationError(
                        f'Ya existe un semestre con el número {value}.'
                    )
        return value
    
    def create(self, validated_data):
        """
        Sobrescribir create para manejar el error de integridad
        """
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            if "unique constraint" in str(e).lower():
                if 'numero' in str(e).lower():
                    raise serializers.ValidationError({
                        'error': 'Ya existe un semestre con ese número.'
                    })
                raise serializers.ValidationError({
                    'error': 'Ya existe un semestre con esos datos.'
                })
            raise e


class EstudianteSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para mostrar información adicional
    nombre_completo = serializers.CharField(read_only=True)
    # Usar SemestreSerializer para mostrar el semestre como objeto anidado
    semestre_actual = SemestreSerializer(read_only=True)
    
    class Meta:
        model = Estudiante
        fields = ['id', 'curp', 'nombre', 'apellidos', 'semestre_actual', 
                  'nombre_completo', 'fecha_registro', 'fecha_actualizacion']
        read_only_fields = ['fecha_registro', 'fecha_actualizacion']
        extra_kwargs = {
            'curp': {
                'validators': [],  # Eliminar los validadores automáticos
                'error_messages': {
                    'unique': 'Ya existe un estudiante con esa CURP.',
                }
            }
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar el validador UniqueValidator para CURP
        if hasattr(self, 'fields'):
            curp_field = self.fields.get('curp')
            if curp_field:
                # Filtrar y eliminar el validador UniqueValidator
                curp_field.validators = [
                    v for v in curp_field.validators 
                    if not (hasattr(v, 'code') and v.code == 'unique')
                ]
    
    def validate_curp(self, value):
        """
        Validación personalizada para CURP única
        """
        # Verificar si ya existe un estudiante con esta CURP
        if not self.instance:  # Para creación
            if Estudiante.objects.filter(curp=value).exists():
                raise serializers.ValidationError(
                    f'Ya existe un estudiante con la CURP {value}.'
                )
        else:  # Para actualización
            if value != self.instance.curp:
                if Estudiante.objects.filter(curp=value).exists():
                    raise serializers.ValidationError(
                        f'Ya existe un estudiante con la CURP {value}.'
                    )
        return value
    
    def validate(self, data):
        """
        Validaciones adicionales
        """
        # Para creación/actualización, semestre_actual debe ser un ID
        # El campo es read_only en la respuesta, pero para escritura recibe un ID
        return data
    
    def create(self, validated_data):
        """
        Sobrescribir create para manejar el error de integridad
        """
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            if "unique constraint" in str(e).lower():
                if "curp" in str(e).lower():
                    raise serializers.ValidationError({
                        'error': 'Ya existe un estudiante con esa CURP.'
                    })
                raise serializers.ValidationError({
                    'error': 'Ya existe un registro con estos datos'
                })
            raise e


class NotaSerializer(serializers.ModelSerializer):
    """Serializer para Nota con todas las relaciones anidadas"""
    # Usar los serializers completos para cada relación
    estudiante = EstudianteSerializer(read_only=True)
    asignatura = AsignaturaSerializer(read_only=True)
    semestre_cursado = SemestreSerializer(read_only=True)
    
    # Campos para escritura (solo IDs)
    estudiante_id = serializers.PrimaryKeyRelatedField(
        queryset=Estudiante.objects.all(),
        source='estudiante',
        write_only=True
    )
    asignatura_id = serializers.PrimaryKeyRelatedField(
        queryset=Asignatura.objects.all(),
        source='asignatura',
        write_only=True
    )

    nota = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2,
        min_value=Decimal('0.0'),
        max_value=Decimal('100.0'),
        required=True
    )
    
    class Meta:
        model = Nota
        fields = [
            'id', 'estudiante', 'estudiante_id', 
            'asignatura', 'asignatura_id',
            'semestre_cursado', 'nota',
            'fecha_registro', 'fecha_actualizacion'
        ]
        read_only_fields = ['semestre_cursado', 'fecha_registro', 'fecha_actualizacion']
    
    def validate(self, data):
        """
        Validación personalizada para evitar el error de unique_together
        """
        # Para escritura, obtenemos los objetos de los campos write_only
        estudiante = data.get('estudiante')  # Viene de estudiante_id
        asignatura = data.get('asignatura')  # Viene de asignatura_id
        
        if not self.instance:  # Creación
            if estudiante and asignatura:
                semestre_actual = estudiante.semestre_actual
                
                if Nota.objects.filter(
                    estudiante=estudiante,
                    asignatura=asignatura,
                    semestre_cursado=semestre_actual
                ).exists():
                    raise serializers.ValidationError({
                        'error': f'El estudiante {estudiante.nombre} {estudiante.apellidos} ya tiene una nota en {asignatura.nombre} para el {semestre_actual.get_numero_display()}.'
                    })
                
                # Asignar el semestre cursado automáticamente
                data['semestre_cursado'] = semestre_actual
        
        else:  # Actualización
            estudiante_actual = estudiante or self.instance.estudiante
            asignatura_actual = asignatura or self.instance.asignatura
            
            if estudiante != self.instance.estudiante or asignatura != self.instance.asignatura:
                semestre_actual = estudiante_actual.semestre_actual
                
                if Nota.objects.filter(
                    estudiante=estudiante_actual,
                    asignatura=asignatura_actual,
                    semestre_cursado=semestre_actual
                ).exclude(pk=self.instance.pk).exists():
                    raise serializers.ValidationError({
                        'error': 'Ya existe una nota para este estudiante, asignatura y semestre.'
                    })
                
                # Actualizar el semestre cursado si cambió el estudiante
                if estudiante != self.instance.estudiante:
                    data['semestre_cursado'] = semestre_actual
        
        return data
    
    def create(self, validated_data):
        """
        Sobrescribir create para manejar el error de integridad
        """
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            if "unique constraint" in str(e).lower():
                raise serializers.ValidationError({
                    'error': 'No se puede crear la nota porque ya existe una para este estudiante, asignatura y semestre.'
                })
            raise e
    
    def to_representation(self, instance):
        """
        Personalizar la representación de los datos
        """
        representation = super().to_representation(instance)
        return representation
