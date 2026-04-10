from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator

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

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if extra_fields.get('user_type') == 'admin' and not username:
            raise ValueError('El administrador debe tener un username')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('admin', 'Administrador'),
        ('student', 'Estudiante'),
    )
    
    # Campos comunes
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    first_name = models.CharField('nombre', max_length=150, blank=True)
    last_name = models.CharField('apellidos', max_length=150, blank=True)
    password = models.CharField(max_length=128)
    
    # Campos específicos para estudiante (actualizados)
    curp = models.CharField(
        max_length=18,
        unique=True,
        blank=True,
        null=True,
        verbose_name='CURP',
        validators=[RegexValidator(r'^[A-Z]{4}\d{6}[A-Z]{6}\d{2}$', 'CURP inválida')]
    )
    semestre_actual = models.ForeignKey(
        'Semestre',
        on_delete=models.PROTECT,
        related_name='estudiantes_actuales',
        verbose_name='Semestre actual',
        null=True,
        blank=True
    )
    numero_control = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    # Tipo de usuario y permisos
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        if self.user_type == 'admin':
            return f"{self.username} (Admin)"
        return f"{self.numero_control} (Estudiante)"
    
    def save(self, *args, **kwargs):
        if self.user_type == 'admin':
            if not self.username:
                raise ValueError("El administrador debe tener un username")
            self.numero_control = None
            self.curp = None
            self.semestre_actual = None
            self.is_staff = True
        else:  # student
            if not self.numero_control:
                raise ValueError("El estudiante debe tener un número de control")
            self.username = None
            #self.first_name = ''
            #self.last_name = ''
            # curp y semestre_actual pueden ser nulos
            self.is_staff = False
            self.is_superuser = False
        super().save(*args, **kwargs)

