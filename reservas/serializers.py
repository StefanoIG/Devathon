from rest_framework import serializers
from .models import Reserva
from mesas.models import Mesa
from mesas.serializers import MesaSerializer

class ReservaSerializer(serializers.ModelSerializer):
    mesa = MesaSerializer(read_only=True)
    mesa_id = serializers.PrimaryKeyRelatedField(queryset=Mesa.objects.all(), source='mesa', write_only=True)

    class Meta:
        model = Reserva
        fields = ['id', 'cliente', 'empleado', 'mesa', 'mesa_id', 'fecha_reserva', 'hora_reserva', 'estado']
        read_only_fields = ['id', 'cliente', 'estado']

    def create(self, validated_data):
        mesa = validated_data.pop('mesa')
        reserva = Reserva.objects.create(mesa=mesa, **validated_data)
        return reserva
