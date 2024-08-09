from django.db import models
#importar modelos de usuarios, mesas y empleados
from mesas.models import Mesa
from usuarios.models import Cliente
from empleados.models import Empleado


# Create your models here.
class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='reservas')
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas_asignadas')
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    fecha_reserva = models.DateField()
    hora_reserva = models.TimeField()
    is_active = models.BooleanField(default=True)  # Soft delete field
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()
        return True
    


    def __str__(self):
        return f"Reserva {self.id} - {self.cliente.nombre} - {self.fecha_reserva} {self.hora_reserva}"