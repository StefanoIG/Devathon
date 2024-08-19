from django.db import models
#importar modelos de usuarios, mesas y empleados
from mesas.models import Mesa
from usuarios.models import Cliente
from empleados.models import Empleado
#importar timedelta para calcular la hora_fin_reserva
from datetime import timedelta, datetime

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
    tiempo_reserva= models.IntegerField(default=60);    #tiempo_reserva se le suma 60 minutos a la hora reserva como default, es decir, si el cliente da la hora bien y si no se le suma 60 minutos
    hora_fin_reserva= models.TimeField(null=True, blank=True); #hora_fin_reserva se calcula en base a la hora_reserva y tiempo_reserva
    is_active = models.BooleanField(default=True)  # Soft delete field

    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()
        return True
    #funcion trigger que calcula la hora_fin_reserva en base a la hora_reserva y tiempo_reserva
    def save(self, *args, **kwargs):
        # Asegúrate de que fecha_reserva sea un objeto datetime.date
        if isinstance(self.fecha_reserva, str):
            self.fecha_reserva = datetime.strptime(self.fecha_reserva, '%Y-%m-%d').date()
        
        # Asegúrate de que hora_reserva sea un objeto datetime.time
        if isinstance(self.hora_reserva, str):
            self.hora_reserva = datetime.strptime(self.hora_reserva, '%H:%M:%S').time()

        # Convierte fecha_reserva y hora_reserva en un objeto datetime
        reserva_datetime = datetime.combine(self.fecha_reserva, self.hora_reserva)
        
        # Suma el tiempo de reserva para calcular hora_fin_reserva
        fin_reserva_datetime = reserva_datetime + timedelta(minutes=self.tiempo_reserva)
        
        # Extrae la hora de fin de la reserva
        self.hora_fin_reserva = fin_reserva_datetime.time()
        
        super(Reserva, self).save(*args, **kwargs)


    


    def __str__(self):
        return f"Reserva {self.id} - {self.cliente.nombre} - {self.fecha_reserva} {self.hora_reserva}"