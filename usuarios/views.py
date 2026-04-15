from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from .filters import *

from .serializers import *

User = get_user_model()


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# api/views.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import CustomTokenObtainPairSerializer
'''
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

'''


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ResetPasswordSerializer(data={}, context={'user': user, 'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Contraseña restablecida exitosamente.",
                "new_password": user.numero_control if user.user_type == 'student' else user.username
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Contraseña actualizada correctamente."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            errors = serializer.errors
            error_msg = None
            
            # Prioridad: errores generales (non_field_errors)
            if 'non_field_errors' in errors:
                error_msg = errors['non_field_errors'][0]
            else:
                # Si hay errores en campos específicos (username, password, etc.)
                # los concatenamos en un solo mensaje legible
                field_messages = []
                for field, messages in errors.items():
                    # messages puede ser una lista, tomamos el primero
                    field_messages.append(f"{messages[0]}")
                error_msg = ' / '.join(field_messages) if field_messages else 'Error de validación'
            
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
        
        # Si todo es correcto, devolvemos los datos del serializer
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
'''
class LoginView(APIView):
    permission_classes = []  # acceso público

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = serializer.validated_data['token']
            # Datos básicos del usuario
            user_data = {
                'id': user.id,
                'tipo': user.user_type,
                'token': token,
            }
            if user.user_type == 'admin':
                user_data['username'] = user.username
                user_data['nombre'] = user.first_name
                user_data['apellidos'] = user.last_name
            else:
                user_data['nombre'] = user.first_name
                user_data['apellidos'] = user.last_name
                user_data['numero_control'] = user.numero_control
                user_data['curp'] = user.curp
                user_data['semestre'] = user.semestre_actual.numero if user.semestre_actual else None
            return Response(user_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
'''


class LoginView(APIView):
    permission_classes = []  # acceso público

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        print('inico')
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = serializer.validated_data['token']
            # Datos básicos del usuario
            user_data = {
                'id': user.id,
                'tipo': user.user_type,
                'token': token,
            }
            if user.user_type == 'admin':
                user_data['username'] = user.username
                user_data['nombre'] = user.first_name
                user_data['apellidos'] = user.last_name
            else:
                user_data['nombre'] = user.first_name
                user_data['apellidos'] = user.last_name
                user_data['numero_control'] = user.numero_control
                user_data['curp'] = user.curp
                user_data['semestre'] = user.semestre_actual.numero if user.semestre_actual else None
            return Response(user_data, status=status.HTTP_200_OK)

        # --- MEJORA: hacer legibles TODOS los errores ---
        errors = serializer.errors
        custom_errors = {}
        print(errors)
        print('sigue')

        for field, messages in errors.items():
            print(field)
            if field == 'non_field_errors':
                # Extraer el primer mensaje y personalizarlo
                raw_msg = messages[0] if messages else ''
                if 'inválidas' in raw_msg.lower() or 'credenciales' in raw_msg.lower():
                    custom_errors['error'] = 'Credenciales incorrectas. Por favor, verifica tu usuario y contraseña.'
                elif 'inactivo' in raw_msg.lower():
                    custom_errors['error'] = 'Tu cuenta está desactivada. Contacta al administrador.'
                else:
                    custom_errors['error'] = raw_msg  # fallback
            elif field == 'username':
                # Mensaje más claro para el campo username
                custom_errors['username'] = 'El nombre de usuario o número de control es obligatorio.'
            elif field == 'password':
                # Mensaje más claro para el campo password
                custom_errors['password'] = 'La contraseña es obligatoria.'
            else:
                # Cualquier otro campo (no debería ocurrir)
                custom_errors[field] = messages

        return Response(custom_errors, status=status.HTTP_400_BAD_REQUEST)

# 2. ViewSet para Administradores (user_type='admin')
class AdminViewSet(viewsets.ModelViewSet):
    """
    CRUD completo para usuarios tipo Administrador.
    Solo accesible para superusuarios (is_staff o is_superuser).
    """
    queryset = User.objects.filter(user_type='admin')
    serializer_class = AdminSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdminFilter

    def perform_create(self, serializer):
        serializer.save(user_type='admin', is_superuser=True)   # ← agregar is_superuser=True


