from django.db import models
from reservas.models import Reserva
from usuarios.models import Cliente
from datetime import timedelta
from django.utils import timezone

def get_default_fecha_vencimiento():
    return timezone.now().date() + timedelta(days=30)

class Factura(models.Model):
    ESTADO_FACTURA_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADA', 'Pagada'),
        ('CANCELADA', 'Cancelada'),
    ]

    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='factura')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='facturas')
    fecha_emision = models.DateField(auto_now_add=True)
    fecha_vencimiento = models.DateField(default=get_default_fecha_vencimiento)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADO_FACTURA_CHOICES, default='PENDIENTE')
    is_active = models.BooleanField(default=True)  # Soft delete field

    def __str__(self):
        return f"Factura {self.id} - {self.cliente.nombre} - {self.monto_total} - {self.estado}"

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()
        return True
