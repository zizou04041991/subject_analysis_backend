from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

class Semestre(models.Model):
    """Modelo para gestionar los semestres académicos"""
    
    numero = models.IntegerField(
        unique=True,  # Ahora es único pero no es llave primaria
        verbose_name="Semestre"
    )
    
    class Meta:
        ordering = ['numero']
        verbose_name = "Semestre"
        verbose_name_plural = "Semestres"
    
    def __str__(self):
        return f"{self.numero}° Semestre"
    
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

# models.py - Actualizar el modelo Estudiante
class Estudiante(models.Model):
    curp = models.CharField(max_length=18, unique=True, verbose_name="CURP")
    nombre = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=100)
    semestre_actual = models.ForeignKey(
        Semestre, 
        on_delete=models.PROTECT, 
        related_name='estudiantes_actuales',
        verbose_name="Semestre actual",
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
        ordering = ['apellidos', 'nombre']

    def __str__(self):
        return f"{self.nombre} {self.apellidos} - {self.curp}"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del estudiante"""
        return f"{self.nombre} {self.apellidos}".strip()
    
    @property
    def curp_completo(self):
        """Retorna la CURP del estudiante"""
        return self.curp

class Nota(models.Model):
    estudiante = models.ForeignKey(
        Estudiante, 
        on_delete=models.CASCADE, 
        related_name='notas'
    )
    asignatura = models.ForeignKey(
        Asignatura, 
        on_delete=models.CASCADE, 
        related_name='notas'
    )
    semestre_cursado = models.ForeignKey(
        Semestre,
        on_delete=models.PROTECT,
        related_name='notas',
        verbose_name="Semestre en que cursó",
        editable=False
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
        unique_together = ['estudiante', 'asignatura', 'semestre_cursado']
        ordering = ['estudiante', 'asignatura']

    def __str__(self):
        return f"{self.estudiante} - {self.asignatura} - {self.semestre_cursado}: {self.nota}"
    
    def save(self, *args, **kwargs):
        # Si no tiene semestre cursado asignado, usar el semestre actual del estudiante
        if not self.semestre_cursado_id and self.estudiante:
            self.semestre_cursado = self.estudiante.semestre_actual
        
        # Verificar que ya tenga semestre cursado antes de guardar
        if not self.semestre_cursado_id:
            raise ValueError("No se pudo determinar el semestre cursado. El estudiante debe tener un semestre actual.")
        
        super().save(*args, **kwargs)