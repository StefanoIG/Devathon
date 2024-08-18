from django.db import models

class Mesa(models.Model):
    ESTADO_OPCIONES = [
        ('activa', 'Activa'),
        ('en_mantenimiento', 'En mantenimiento'),
        ('reservada', 'Reservada'),
    ]

    numero = models.IntegerField()
    capacidad = models.IntegerField()
    estado = models.CharField(
        max_length=50,
        choices=ESTADO_OPCIONES,
        default='activa'
    )
    is_activate = models.BooleanField(default=True)

    def __str__(self):
        return f'Mesa {self.numero} - {self.get_estado_display()}'
