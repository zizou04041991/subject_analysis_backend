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
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notas',
        limit_choices_to={'user_type': 'student'},
        verbose_name="Estudiante"
    )
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE, related_name='notas')
    semestre = models.ForeignKey(  # único campo
        'usuarios.Semestre',
        on_delete=models.PROTECT,
        related_name='notas',
        verbose_name="Semestre"
    )
    tcp = models.ForeignKey('TCP', on_delete=models.PROTECT, related_name='notas')
    nota = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['estudiante', 'tcp', 'semestre', 'asignatura']
        ordering = ['estudiante', 'asignatura']

    def save(self, *args, **kwargs):
        if not self.semestre_id and self.estudiante:
            if self.estudiante.semestre_actual:
                self.semestre = self.estudiante.semestre_actual
            else:
                raise ValueError("El estudiante no tiene semestre actual.")
        super().save(*args, **kwargs)