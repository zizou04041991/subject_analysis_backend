from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from .serializers import *

User = get_user_model()


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


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
                user_data['numero_control'] = user.numero_control
                user_data['curp'] = user.curp
                user_data['semestre'] = user.semestre_actual.numero if user.semestre_actual else None
            return Response(user_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2. ViewSet para Administradores (user_type='admin')
class AdminViewSet(viewsets.ModelViewSet):
    """
    CRUD completo para usuarios tipo Administrador.
    Solo accesible para superusuarios (is_staff o is_superuser).
    """
    queryset = User.objects.filter(user_type='admin')
    serializer_class = AdminSerializer
    #permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(user_type='admin', is_superuser=True)   # ← agregar is_superuser=True


