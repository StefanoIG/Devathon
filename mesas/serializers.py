from rest_framework import serializers
from .models import Mesa

class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = '__all__'


# Definir un serializer solo para los clientes con los campos necesarios
class ClienteMesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = ['numero', 'capacidad', 'estado']