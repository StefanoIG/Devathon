from django.db import models

# Create your models here.

class Mesa(models.Model):
    numero = models.IntegerField()
    capacidad = models.IntegerField()
    estado = models.CharField(max_length=50)
    
    def __str__(self):
        return str(self.numero) + ' ' + str(self.capacidad) + ' ' + str(self.estado)
    