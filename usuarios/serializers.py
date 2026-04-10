# serializers.py
from rest_framework import serializers
from .models import *

from django.contrib.auth import get_user_model


User = get_user_model()


from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

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