# filters.py
from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

User = get_user_model()

class AdminFilter(filters.FilterSet):
    # Filtros case-insensitive "contains" para cada campo
    username = filters.CharFilter(field_name='username', lookup_expr='icontains')
    first_name = filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name = filters.CharFilter(field_name='last_name', lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']