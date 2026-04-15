from rest_framework import serializers
from .models import *
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import *
from usuarios.models import *

from usuarios.models import *  # importa el modelo Usuario
from usuarios.serializers import *  # importa el modelo Usuario


# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()

class PaginacionPersonalizada(PageNumberPagination):
    page_size = 2  # Elementos por página
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
        extra_kwargs = {
            'nombre': {
                'validators': [],  # Eliminar validadores automáticos
                'error_messages': {
                    'unique': 'Ya existe una asignatura con el nombre {nombre}.',
                    'required': 'El campo nombre es obligatorio.',
                    'blank': 'El nombre no puede estar vacío.',
                    'max_length': 'El nombre no puede exceder los 100 caracteres.'
                }
            },
            'color': {
                'error_messages': {
                    'max_length': 'El código de color debe tener exactamente 7 caracteres (incluyendo #).',
                    'min_length': 'El código de color debe tener exactamente 7 caracteres (incluyendo #).'
                }
            }
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar el validador UniqueValidator para nombre
        if hasattr(self, 'fields'):
            nombre_field = self.fields.get('nombre')
            if nombre_field:
                nombre_field.validators = [
                    v for v in nombre_field.validators 
                    if not (hasattr(v, 'code') and v.code == 'unique')
                ]
    
    def validate_nombre(self, value):
        """
        Validación personalizada para nombre único
        """
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        
        # Limpiar el valor
        value = value.strip()
        
        # Verificar unicidad
        if not self.instance:  # Para creación
            if Asignatura.objects.filter(nombre__iexact=value).exists():
                raise serializers.ValidationError(
                    f'Ya existe una asignatura con el nombre "{value}".'
                )
        else:  # Para actualización
            if value.lower() != self.instance.nombre.lower():
                if Asignatura.objects.filter(nombre__iexact=value).exists():
                    raise serializers.ValidationError(
                        f'Ya existe una asignatura con el nombre "{value}".'
                    )
        return value
    
    def validate_color(self, value):
        """
        Validación personalizada para código de color HEX
        """
        if value:
            value = value.upper().strip()
            
            # Validar formato HEX
            import re
            hex_pattern = r'^#([A-Fa-f0-9]{6})$'
            if not re.match(hex_pattern, value):
                raise serializers.ValidationError(
                    'El color debe estar en formato HEX válido (ej: #FF5733).'
                )
        
        return value
    
    def create(self, validated_data):
        """
        Sobrescribir create para manejar el error de integridad
        """
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
                if "nombre" in str(e).lower():
                    nombre = validated_data.get('nombre', 'desconocido')
                    raise serializers.ValidationError({
                        'error': f'Ya existe una asignatura con el nombre "{nombre}".'
                    })
                raise serializers.ValidationError({
                    'error': 'Ya existe un registro con estos datos'
                })
            raise e
    
    def update(self, instance, validated_data):
        """
        Sobrescribir update para manejar el error de integridad
        """
        try:
            return super().update(instance, validated_data)
        except IntegrityError as e:
            if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
                if "nombre" in str(e).lower():
                    nombre = validated_data.get('nombre', instance.nombre)
                    raise serializers.ValidationError({
                        'error': f'Ya existe una asignatura con el nombre "{nombre}".'
                    })
                raise serializers.ValidationError({
                    'error': 'Ya existe un registro con estos datos'
                })
            raise e



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







# serializers.py (parte de EstudianteSerializer)

'''
class EstudianteSerializer(serializers.ModelSerializer):
    # Usar SemestreSerializer para mostrar el semestre como objeto anidado
    semestre_actual = SemestreSerializer(read_only=True)

    # Para escritura: aceptar el ID del semestre
    semestre_id = serializers.PrimaryKeyRelatedField(
        source='semestre_actual',
        queryset=Semestre.objects.all(),
        write_only=True,
        required=False,
        error_messages={
            'does_not_exist': 'El semestre con ID {value} no existe.',
            'incorrect_type': 'Debe proporcionar un ID válido para el semestre.'
        }
    )
    
    # Campos de solo lectura para mostrar información adicional
    nombre_completo = serializers.CharField(read_only=True)
    
    class Meta:
        model = Estudiante
        fields = [
            'id', 'numero_control', 'curp', 'nombre', 'apellidos', 
            'semestre_actual', 'semestre_id',
            'nombre_completo', 'fecha_registro', 'fecha_actualizacion'
        ]
        read_only_fields = ['fecha_registro', 'fecha_actualizacion']
        extra_kwargs = {
            'numero_control': {
                'validators': [],  # Eliminar validadores automáticos
                'error_messages': {
                    'unique': 'Ya existe un estudiante con el número de control {numero_control}.',
                    'required': 'El campo número de control es obligatorio.',
                    'blank': 'El número de control no puede estar vacío.',
                    'max_length': 'El número de control debe tener exactamente 14 dígitos.',
                    'min_length': 'El número de control debe tener exactamente 14 dígitos.'
                }
            },
            'curp': {
                'validators': [],  # Eliminar validadores automáticos
                'error_messages': {
                    'unique': 'Ya existe un estudiante con la CURP {curp}.',
                    'required': 'El campo CURP es obligatorio.',
                    'blank': 'La CURP no puede estar vacía.',
                    'max_length': 'La CURP debe tener exactamente 18 caracteres.',
                    'min_length': 'La CURP debe tener exactamente 18 caracteres.'
                }
            },
            'nombre': {
                'error_messages': {
                    'required': 'El campo nombre es obligatorio.',
                    'blank': 'El nombre no puede estar vacío.'
                }
            },
            'apellidos': {
                'error_messages': {
                    'required': 'El campo apellidos es obligatorio.',
                    'blank': 'Los apellidos no pueden estar vacíos.'
                }
            }
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar validadores UniqueValidator para campos únicos
        if hasattr(self, 'fields'):
            # Para número de control
            numero_control_field = self.fields.get('numero_control')
            if numero_control_field:
                numero_control_field.validators = [
                    v for v in numero_control_field.validators 
                    if not (hasattr(v, 'code') and v.code == 'unique')
                ]
            
            # Para CURP
            curp_field = self.fields.get('curp')
            if curp_field:
                curp_field.validators = [
                    v for v in curp_field.validators 
                    if not (hasattr(v, 'code') and v.code == 'unique')
                ]
    
    def validate_numero_control(self, value):
        """
        Validación personalizada para número de control único de 14 dígitos
        """
        if not value or not str(value).strip():
            raise serializers.ValidationError("El número de control no puede estar vacío.")
        
        # Convertir a string y limpiar
        value = str(value).strip()
        
        # Validar que sean exactamente 14 dígitos
        if not value.isdigit():
            raise serializers.ValidationError("El número de control debe contener solo dígitos.")
        
        if len(value) != 14:
            raise serializers.ValidationError("El número de control debe tener exactamente 14 dígitos.")
        
        # Verificar unicidad
        if not self.instance:  # Para creación
            if Estudiante.objects.filter(numero_control=value).exists():
                raise serializers.ValidationError(
                    f'Ya existe un estudiante con el número de control {value}.'
                )
        else:  # Para actualización
            if value != self.instance.numero_control:
                if Estudiante.objects.filter(numero_control=value).exists():
                    raise serializers.ValidationError(
                        f'Ya existe un estudiante con el número de control {value}.'
                    )
        return value
    
    def validate_curp(self, value):
        """
        Validación personalizada para CURP única
        """
        if not value or not value.strip():
            raise serializers.ValidationError("La CURP no puede estar vacía.")
        
        # Validar formato de CURP (opcional - 18 caracteres alfanuméricos)
        value = value.upper().strip()
        if len(value) != 18:
            raise serializers.ValidationError("La CURP debe tener exactamente 18 caracteres.")
        
        if not value.isalnum():
            raise serializers.ValidationError("La CURP solo puede contener letras y números.")
        
        # Verificar unicidad
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
        Validaciones adicionales y soporte para semestre_actual_id
        """
        request = self.context.get('request')
        
        # Manejar semestre (puede venir como semestre_id o semestre_actual_id)
        semestre_id = None
        
        if request:
            # Verificar si enviaron semestre_actual_id
            if 'semestre_actual_id' in request.data:
                try:
                    semestre_id = int(request.data.get('semestre_actual_id'))
                except (ValueError, TypeError):
                    raise serializers.ValidationError({
                        'semestre_actual_id': 'El campo semestre_actual_id debe ser un número entero válido.'
                    })
            # Verificar si enviaron semestre_id
            elif 'semestre_id' in request.data:
                try:
                    semestre_id = int(request.data.get('semestre_id'))
                except (ValueError, TypeError):
                    raise serializers.ValidationError({
                        'semestre_id': 'El campo semestre_id debe ser un número entero válido.'
                    })
        
        # Si encontramos un semestre_id, validar que exista y asignarlo
        if semestre_id is not None:
            try:
                semestre = Semestre.objects.get(pk=semestre_id)
                data['semestre_actual'] = semestre
            except Semestre.DoesNotExist:
                raise serializers.ValidationError({
                    'semestre_id' if 'semestre_id' in request.data else 'semestre_actual_id': 
                    f'El semestre con ID {semestre_id} no existe.'
                })
        else:
            # Si no hay semestre en la petición, verificar si es creación o actualización
            if not self.instance:  # Creación - semestre es obligatorio
                raise serializers.ValidationError({
                    'semestre_id': 'El campo semestre_id o semestre_actual_id es obligatorio.'
                })
            # En actualización, si no viene semestre, mantener el actual
            
        return data
    
    def create(self, validated_data):
        """
        Sobrescribir create para manejar el error de integridad
        """
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
                error_str = str(e).lower()
                if "numero_control" in error_str:
                    numero_control = validated_data.get('numero_control', 'desconocida')
                    raise serializers.ValidationError({
                        'error': f'Ya existe un estudiante con el número de control {numero_control}.'
                    })
                elif "curp" in error_str:
                    curp_value = validated_data.get('curp', 'desconocida')
                    raise serializers.ValidationError({
                        'error': f'Ya existe un estudiante con la CURP {curp_value}.'
                    })
                raise serializers.ValidationError({
                    'error': 'Ya existe un registro con estos datos'
                })
            raise e
    
    def update(self, instance, validated_data):
        """
        Sobrescribir update para manejar el error de integridad
        """
        try:
            return super().update(instance, validated_data)
        except IntegrityError as e:
            if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
                error_str = str(e).lower()
                if "numero_control" in error_str:
                    numero_control = validated_data.get('numero_control', instance.numero_control)
                    raise serializers.ValidationError({
                        'error': f'Ya existe un estudiante con el número de control {numero_control}.'
                    })
                elif "curp" in error_str:
                    curp_value = validated_data.get('curp', instance.curp)
                    raise serializers.ValidationError({
                        'error': f'Ya existe un estudiante con la CURP {curp_value}.'
                    })
                raise serializers.ValidationError({
                    'error': 'Ya existe un registro con estos datos'
                })
            raise e
'''
class EstudianteSerializer(UserBaseSerializer):
    semestre_actual = serializers.PrimaryKeyRelatedField(
        queryset=Semestre.objects.all(),
        required=False,
        allow_null=True
    )
    # Opcional: mostrar el número del semestre
    semestre_numero = serializers.SerializerMethodField(read_only=True)

    class Meta(UserBaseSerializer.Meta):
        model = User
        fields = [
            'id', 'numero_control', 'curp', 'semestre_actual', 'semestre_numero', 'first_name', 'last_name',  # ← agregar estos campos
            'password', 'user_type'
        ]
        read_only_fields = ['user_type']

    def get_semestre_numero(self, obj):
        return obj.semestre_actual.numero if obj.semestre_actual else None

    def validate(self, data):
        data['user_type'] = 'student'
        if not data.get('numero_control'):
            raise serializers.ValidationError({"numero_control": "El estudiante debe tener número de control."})
        # Validar formato CURP (opcional, ya lo hace el modelo)
        curp = data.get('curp')
        if curp and not self._validate_curp_format(curp):
            raise serializers.ValidationError({"curp": "CURP inválida."})
        return data

    def _validate_curp_format(self, curp):
        import re
        pattern = r'^[A-Z]{4}\d{6}[A-Z]{6}\d{2}$'
        return bool(re.match(pattern, curp))
    
class TCPSerializer(serializers.ModelSerializer):
    """Serializer para TCP"""
    
    class Meta:
        model = TCP
        fields = ['id', 'numero', 'fecha_creacion', 'fecha_actualizacion']
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']
        extra_kwargs = {
            'numero': {
                'validators': [],  # Eliminar validadores automáticos
                'error_messages': {
                    'unique': 'ya existe este tcp con numero {numero}',
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
        Validación personalizada para el número de TCP
        """
        # Verificar si ya existe un TCP con este número (validación manual)
        if not self.instance:  # Para creación
            if TCP.objects.filter(numero=value).exists():
                raise serializers.ValidationError(
                    f'ya existe este tcp con numero {value}'
                )
        else:  # Para actualización
            if value != self.instance.numero:
                if TCP.objects.filter(numero=value).exists():
                    raise serializers.ValidationError(
                        f'ya existe este tcp con numero {value}'
                    )
        return value
    
    def create(self, validated_data):
        """
        Sobrescribir create para manejar el error de integridad
        """
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
                if 'numero' in str(e).lower():
                    raise serializers.ValidationError({
                        'error': f'ya existe este tcp con numero {validated_data.get("numero")}'
                    })
                raise serializers.ValidationError({
                    'error': 'Ya existe un TCP con esos datos.'
                })
            raise e
    
    def update(self, instance, validated_data):
        """
        Sobrescribir update para manejar el error de integridad
        """
        try:
            return super().update(instance, validated_data)
        except IntegrityError as e:
            if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
                if 'numero' in str(e).lower():
                    raise serializers.ValidationError({
                        'error': f'Ya existe este tcp con numero {validated_data.get("numero")}'
                    })
                raise serializers.ValidationError({
                    'error': 'Ya existe un TCP con esos datos.'
                })
            raise e




# serializers.py
class NotaSerializer(serializers.ModelSerializer):
    estudiante_nombre_completo = serializers.SerializerMethodField()
    asignatura_nombre = serializers.CharField(source='asignatura.nombre', read_only=True)
    asignatura_color = serializers.CharField(source='asignatura.color', read_only=True)
    semestre_numero = serializers.IntegerField(source='semestre.numero', read_only=True)
    tcp_numero = serializers.IntegerField(source='tcp.numero', read_only=True)
    
    # Hacemos semestre de solo lectura para que no sea requerido en el input
    semestre = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Nota
        fields = [
            'id', 'estudiante', 'estudiante_nombre_completo',
            'asignatura', 'asignatura_nombre', 'asignatura_color',
            'semestre', 'semestre_numero',
            'tcp', 'tcp_numero',
            'nota', 'fecha_registro', 'fecha_actualizacion'
        ]
        read_only_fields = ['fecha_registro', 'fecha_actualizacion']

    def get_estudiante_nombre_completo(self, obj):
        return f"{obj.estudiante.last_name} {obj.estudiante.first_name}".strip()

    def validate(self, data):
        estudiante = data.get('estudiante')
        tcp = data.get('tcp')
        asignatura = data.get('asignatura')

        # Validar campos obligatorios
        if not all([estudiante, tcp, asignatura]):
            return data

        # Obtener semestre actual del estudiante
        semestre = estudiante.semestre_actual
        if not semestre:
            raise serializers.ValidationError(
                "El estudiante no tiene un semestre actual. Asigne un semestre al estudiante."
            )

        # Verificar unicidad
        existe = Nota.objects.filter(
            estudiante=estudiante,
            tcp=tcp,
            semestre=semestre,
            asignatura=asignatura
        )
        if self.instance:
            existe = existe.exclude(pk=self.instance.pk)

        if existe.exists():
            raise serializers.ValidationError(
                "Ya existe una calificación para esta combinación de Estudiante, TCP, Semestre y Asignatura."
            )

        # Inyectar el semestre calculado para que se use al guardar
        data['semestre'] = semestre
        return data

    def create(self, validated_data):
        # Aseguramos que semestre esté presente
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)