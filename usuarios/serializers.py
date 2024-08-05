from rest_framework import serializers
from .models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'apellido', 'telefono', 'correo_electronico', 'fecha_registro', 'password']
        read_only_fields = ['id', 'fecha_registro']