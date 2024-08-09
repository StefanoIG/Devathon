import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from threading import Timer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Reserva
from mesas.models import Mesa
from .serializers import ReservaSerializer

# Signal para actualizar el estado de la mesa
@receiver(post_save, sender=Reserva)
def update_mesa_status(sender, instance, **kwargs):
    # Calcular el tiempo restante hasta 5 minutos antes de la reserva
    reserva_datetime = datetime.datetime.combine(instance.fecha_reserva, instance.hora_reserva)
    reserva_datetime = timezone.make_aware(reserva_datetime)
    time_until_update = (reserva_datetime - timezone.now()).total_seconds() - 300  # 5 minutos antes

    if time_until_update > 0:
        # Crear un temporizador que cambie el estado de la mesa en el momento adecuado
        Timer(time_until_update, change_mesa_status, [instance.mesa]).start()

def change_mesa_status(mesa):
    mesa.estado = 'reservada'
    mesa.save()


# Vista para crear una reserva
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_reserva(request):
    cliente = request.user  # Asumimos que el cliente es el usuario autenticado
    data = request.data
    mesa_id = data.get('mesa_id')
    
    try:
        mesa = Mesa.objects.get(id=mesa_id)
    except Mesa.DoesNotExist:
        return Response({"error": "Mesa no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    if mesa.estado == 'reservada':
        return Response({"error": "La mesa ya está reservada"}, status=status.HTTP_400_BAD_REQUEST)

    # Crear la reserva
    reserva = Reserva.objects.create(
        cliente=cliente,
        empleado_id=data.get('empleado_id'),  # Puede ser None
        mesa=mesa,
        fecha_reserva=data.get('fecha_reserva'),
        hora_reserva=data.get('hora_reserva'),
        estado='confirmada'  # O el estado inicial que prefieras
    )

    # No cambiamos el estado de la mesa aquí, se cambiará automáticamente 5 minutos antes de la reserva

    return Response(ReservaSerializer(reserva).data, status=status.HTTP_201_CREATED)


# Vista para cancelar una reserva
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_reserva(request, pk):
    try:
        reserva = Reserva.objects.get(pk=pk, cliente=request.user)
    except Reserva.DoesNotExist:
        return Response({"error": "Reserva no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    # Restaurar el estado de la mesa
    mesa = reserva.mesa
    mesa.estado = 'disponible'
    mesa.save()

    # Eliminar la reserva
    reserva.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
