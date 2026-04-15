# serializers.py
from rest_framework import serializers
from .models import *

from rest_framework.authtoken.models import Token

# api/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class ResetPasswordSerializer(serializers.Serializer):
    def validate(self, attrs):
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError("Usuario no especificado.")
        request = self.context.get('request')
        if request and not request.user.is_staff:
            raise serializers.ValidationError("No tienes permiso para resetear contraseñas.")
        return attrs

    def save(self, **kwargs):
        user = self.context['user']
        if user.user_type == 'student':
            new_password = user.numero_control
            if not new_password:
                raise serializers.ValidationError("El estudiante no tiene número de control asignado.")
        elif user.user_type == 'admin':
            new_password = user.username
            if not new_password:
                raise serializers.ValidationError("El administrador no tiene username asignado.")
        else:
            raise serializers.ValidationError("Tipo de usuario no válido.")
        
        user.set_password(new_password)   # No aplica validadores fuertes
        user.save()
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError('Debe proporcionar usuario y contraseña.')

        # Autenticar usando el backend personalizado (que permite username o numero_control)
        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError('Las credenciales son incorrectas.')

        if not user.is_active:
            raise serializers.ValidationError('El usuario está inactivo.')

        # Generar tokens usando el método de la clase padre
        refresh = self.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'tipo': user.user_type,
                'nombre': user.first_name,
                'apellidos': user.last_name,
            }
        }
        if user.user_type == 'admin':
            data['user']['username'] = user.username
        else:
            data['user']['numero_control'] = user.numero_control
            data['user']['curp'] = user.curp
            data['user']['semestre'] = user.semestre_actual.numero if user.semestre_actual else None

        return data

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="Puede ser username (admin) o número de control (estudiante)")
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError("Debe proporcionar usuario y contraseña.")

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Credenciales inválidas.")

        if not user.is_active:
            raise serializers.ValidationError("Usuario inactivo.")

        # Obtener o crear token
        token, _ = Token.objects.get_or_create(user=user)

        data['user'] = user
        data['token'] = token.key
        return data

class UserBaseSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'password', 'user_type', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
    


class AdminSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'password', 'user_type']
        read_only_fields = ['user_type']

    def validate(self, data):
        data['user_type'] = 'admin'
        if not data.get('username'):
            raise serializers.ValidationError({"username": "El administrador debe tener un username."})
        return data