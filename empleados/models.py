from django.db import models

# Create your models here.
class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    puesto = models.CharField(max_length=100, default='Empleado')
    telefono = models.CharField(max_length=10)
    fecha_contratacion = models.DateField(auto_now_add=True)
    correo_electronico = models.EmailField(max_length=100,unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
