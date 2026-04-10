from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date


# models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
#from django.db import models
from django.core.validators import RegexValidator

from usuarios.models import *
from django.conf import settings

    
class TCP(models.Model):
    """
    Modelo para TCP (Trabajo Común de Prácticas)
    """
    numero = models.IntegerField(
        unique=True,
        verbose_name="Número de TCP",
        help_text="Número único del TCP (ej: 1, 2, 3, etc.)"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "TCP"
        verbose_name_plural = "TCPs"
        ordering = ['numero']

    def __str__(self):
        return f"TCP {self.numero}"


    
class Asignatura(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, help_text="Código de color en formato HEX (ej: #FF5733)", default="#000000")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Asignatura"
        verbose_name_plural = "Asignaturas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Nota(models.Model):
    # Cambio: apunta al modelo de usuario personalizado, solo estudiantes
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL,          # o 'myapp.CustomUser'
        on_delete=models.CASCADE,
        related_name='notas',
        limit_choices_to={'user_type': 'student'},  # solo estudiantes
        verbose_name="Estudiante"
    )
    asignatura = models.ForeignKey(
        'Asignatura', 
        on_delete=models.CASCADE, 
        related_name='notas'
    )
    semestre_cursado = models.ForeignKey(
        'usuarios.Semestre',   # ← CORREGIDO
        on_delete=models.PROTECT,
        related_name='notas',
        verbose_name="Semestre en que cursó",
        editable=False
    )
    tcp = models.ForeignKey(
        'TCP',
        on_delete=models.PROTECT,
        related_name='notas',
        verbose_name="TCP asociado"
    )
    nota = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Nota"
        verbose_name_plural = "Notas"
        unique_together = ['estudiante', 'tcp', 'semestre_cursado', 'asignatura']
        ordering = ['estudiante', 'asignatura']

    def __str__(self):
        return f"{self.estudiante} - {self.asignatura} - TCP: {self.tcp.numero} - {self.semestre_cursado}: {self.nota}"

    def save(self, *args, **kwargs):
        # Validar que tenga TCP
        if not self.tcp_id:
            raise ValueError("El TCP es obligatorio")

        # Verificar que el estudiante sea realmente un usuario tipo 'student'
        if self.estudiante and self.estudiante.user_type != 'student':
            raise ValueError("Solo los usuarios de tipo estudiante pueden tener notas.")

        # Si no tiene semestre cursado asignado, usar el semestre actual del estudiante
        if not self.semestre_cursado_id and self.estudiante:
            # Asegurar que el estudiante tenga semestre_actual (puede ser nulo)
            if hasattr(self.estudiante, 'semestre_actual') and self.estudiante.semestre_actual:
                self.semestre_cursado = self.estudiante.semestre_actual
            else:
                raise ValueError("El estudiante no tiene un semestre actual asignado.")

        # Verificar que ya tenga semestre cursado antes de guardar
        if not self.semestre_cursado_id:
            raise ValueError("No se pudo determinar el semestre cursado. El estudiante debe tener un semestre actual.")

        super().save(*args, **kwargs)