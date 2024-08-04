from django.db import models

# Create your models here.

# Tabla clientes
class Cliente(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('user', 'Usuario'),
        ('empleado', 'Empleado'),
    )
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    telefono = models.CharField(max_length=50)
    correo_electronico = models.EmailField(max_length=50, unique=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.nombre