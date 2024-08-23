from rest_framework import serializers
from .models import Factura

class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = ['id', 'reserva', 'cliente', 'fecha_emision', 'fecha_vencimiento', 'monto_total', 'estado', 'is_active']
