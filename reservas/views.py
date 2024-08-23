import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from threading import Timer
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Reserva
from mesas.models import Mesa
from rest_framework.views import APIView
from .serializers import ReservaSerializer

# Validaciones de hora de reserva solo para clientes
def validate_reservation_time_for_cliente(fecha_reserva, hora_reserva):
    print(f"Validando reserva para la fecha {fecha_reserva} y hora {hora_reserva}")
    
    # Convertir fecha_reserva a un objeto datetime.date si es necesario
    if isinstance(fecha_reserva, str):
        fecha_reserva = datetime.datetime.strptime(fecha_reserva, '%Y-%m-%d').date()
    if isinstance(hora_reserva, str):
        hora_reserva = datetime.datetime.strptime(hora_reserva, '%H:%M:%S').time()

    reserva_datetime = datetime.datetime.combine(fecha_reserva, hora_reserva)
    reserva_datetime = timezone.make_aware(reserva_datetime)  # Hacer el datetime aware
    now = timezone.now()

    print(f"Fecha y hora de la reserva: {reserva_datetime}")
    print(f"Fecha y hora actual: {now}")

    # Validar que la fecha de reserva no sea en el pasado
    if reserva_datetime < now:
        print("Error: No puedes reservar para una fecha o hora pasada.")
        return {"error": "No puedes reservar para una fecha o hora pasada."}

    # Validar que la hora de reserva esté entre las 10:00 AM y las 6:00 PM
    if not (9 <= hora_reserva.hour < 18):
        print("Error: Las reservas solo se permiten entre las 10:00 AM y las 6:00 PM.")
        return {"error": "Las reservas solo se permiten entre las 10:00 AM y las 6:00 PM."}
    
    # Validar que la reserva se haga con al menos 10 minutos de anticipación
    if (reserva_datetime - now).total_seconds() < 600:  # 10 minutos(600 segundos)
        print("Error: Debe reservar con al menos 10 minutos de anticipación.")
        return {"error": "Debe reservar con al menos 10 minutos de anticipación."}
    
    print("Validaciones completadas sin errores")
    return None  # No hay errores de validación

# Enviar correo electrónico de advertencia
def send_warning_email(reserva):
    print(f"Enviando correo de advertencia a {reserva.cliente.correo_electronico}...")
    cliente = reserva.cliente
    subject = 'Advertencia: Tu reserva está por expirar'
    message = (
        f'Estimado {cliente.nombre},\n\n'
        'Tu reserva está por expirar en 30 minutos. Si deseas mantener tu reserva, por favor confirma con un empleado.\n'
        'Si deseas cancelar la reserva, puedes hacerlo haciendo clic en el siguiente enlace:\n'
        f'http://yourdomain.com/cancelar-reserva/{reserva.id}/\n\n'
        'Gracias por utilizar nuestro sistema de reservas.\n\n'
        'Saludos cordiales,\n'
        'Equipo de Reservas'
    )
    send_mail(subject, message, 'noreply@yourdomain.com', [cliente.correo_electronico])
    print("Correo de advertencia enviado con éxito.")

# Cancelar la reserva si no ha sido confirmada después de una hora
def cancel_unconfirmed_reservation(reserva):
    print(f"Cancelando reserva no confirmada ID: {reserva.id}...")
    reserva.refresh_from_db()  # Asegurarse de tener el último estado de la reserva
    if reserva.estado == 'cancelada':
        return  # No hacer nada si la reserva ya fue 
    
    print("Reserva no confirmada. Cancelando...")
    mesa = reserva.mesa
    mesa.estado = 'disponible'
    mesa.save()
    print(f"Mesa {mesa.numero} ahora está en estado 'disponible'.")
    reserva.delete()
    print("Reserva cancelada.")
    # Enviar correo de cancelación
    cliente = reserva.cliente
    print(f"Enviando correo de cancelación a {cliente.correo_electronico}...")
    subject = 'Tu reserva ha sido cancelada'
    message = (
        f'Estimado {cliente.nombre},\n\n'
        'Tu reserva ha sido cancelada porque no fue confirmada por un empleado dentro de una hora.\n'
        'Si necesitas más asistencia, por favor contáctanos.\n\n'
        'Saludos cordiales,\n'
        'Equipo de Reservas'
    )
    send_mail(subject, message, 'noreply@yourdomain.com', [cliente.correo_electronico])
    print("Correo de cancelación enviado con éxito .")

# Cambiar el estado de la mesa a "reservada" 5 minutos antes de la reserva
def set_mesa_as_reserved(reserva):
    reserva.refresh_from_db()
    mesa = reserva.mesa
    mesa.estado = 'Reservada'
    mesa.save()
    print(f"Mesa {mesa.numero} ahora está en estado 'reservada'.")

# Signal para manejar las acciones después de crear una reserva
@receiver(post_save, sender=Reserva)
def handle_reservation(sender, instance, **kwargs):
    print(f"Post Save Signal Triggered for Reservation ID: {instance.id}")
    
    # Convertir fecha_reserva y hora_reserva a datetime.date y datetime.time si es necesario
    if isinstance(instance.fecha_reserva, str):
        instance.fecha_reserva = datetime.datetime.strptime(instance.fecha_reserva, '%Y-%m-%d').date()
    if isinstance(instance.hora_reserva, str):
        instance.hora_reserva = datetime.datetime.strptime(instance.hora_reserva, '%H:%M:%S').time()

    reserva_datetime = datetime.datetime.combine(instance.fecha_reserva, instance.hora_reserva)
    reserva_datetime = timezone.make_aware(reserva_datetime)
    now = timezone.now()

    print(f"Reservation DateTime: {reserva_datetime}")
    print(f"Current DateTime: {now}")

    # Calcular tiempos
    time_until_warning = (reserva_datetime - now).total_seconds() - 100  # 30 minutos antes de la hora de reserva(1800 segundos)
    time_until_cancellation = (reserva_datetime - now).total_seconds() + 120  # 1 hora después de la reserva(3600 segundos)
    time_until_reserved = (reserva_datetime - now).total_seconds() - 300  # 5 minutos antes de la hora de reserva(300 segundos)

    if time_until_warning > 0:
        print(f"Warning Timer set for {time_until_warning} seconds")
        Timer(time_until_warning, send_warning_email, [instance]).start()
    if time_until_cancellation > 0:
        print(f"Cancellation Timer set for {time_until_cancellation} seconds")
        Timer(time_until_cancellation, cancel_unconfirmed_reservation, [instance]).start()
    if time_until_reserved > 0:
        print(f"Reserved Timer set for {time_until_reserved} seconds")
        Timer(time_until_reserved, set_mesa_as_reserved, [instance]).start()

# Vista para crear una reserva
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_reserva(request):
    print("Iniciando creación de reserva...")
    
    cliente = request.user
    data = request.data
    mesa_id = data.get('mesa_id')

    print(f"Cliente: {cliente.nombre}, Mesa ID: {mesa_id}")
    
    try:
        mesa = Mesa.objects.get(id=mesa_id)
    except Mesa.DoesNotExist:
        print("Error: Mesa no encontrada.")
        return Response({"error": "Mesa no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    if mesa.estado == 'reservada':
        print("Error: La mesa ya está reservada.")
        return Response({"error": "La mesa ya está reservada"}, status=status.HTTP_400_BAD_REQUEST)

    # Verificar si la mesa ya está reservada en la misma fecha y hora
    fecha_reserva_str = data.get('fecha_reserva')
    hora_reserva_str = data.get('hora_reserva')

    # Convertir las cadenas a objetos de fecha y hora
    fecha_reserva = datetime.datetime.strptime(fecha_reserva_str, '%Y-%m-%d').date()
    hora_reserva = datetime.datetime.strptime(hora_reserva_str, '%H:%M:%S').time()

    reserva_datetime = datetime.datetime.combine(fecha_reserva, hora_reserva)

    existing_reservas = Reserva.objects.filter(
        mesa=mesa,
        fecha_reserva=fecha_reserva,
        hora_reserva__gte=reserva_datetime.time(),
        hora_reserva__lt=(reserva_datetime + datetime.timedelta(minutes=60)).time()
    )

    if existing_reservas.exists():
        print("Error: La mesa ya tiene una reserva en ese horario.")
        return Response({"error": "La mesa ya tiene una reserva en ese horario."}, status=status.HTTP_400_BAD_REQUEST)

    # Solo aplicar validaciones de tiempo para clientes
    if cliente.rol == 'user':
        print(f"Validando hora de reserva para el cliente {cliente.nombre}")
        validation_error = validate_reservation_time_for_cliente(fecha_reserva, hora_reserva)
        if validation_error:
            print(f"Validation Error: {validation_error}")
            return Response(validation_error, status=status.HTTP_400_BAD_REQUEST)

    # Crear la reserva
    reserva = Reserva.objects.create(
        cliente=cliente,
        empleado_id=data.get('empleado_id'),
        mesa=mesa,
        fecha_reserva=data.get('fecha_reserva'),
        hora_reserva=data.get('hora_reserva'),
        estado='pendiente'
    )
    mesa.estado = 'pendiente'
    mesa.save()

    serializer = ReservaSerializer(reserva)
    print("Reserva creada exitosamente.")
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# Vista para cancelar una reserva
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_reserva(request, pk):
    try:
        reserva = Reserva.objects.get(pk=pk, cliente=request.user)
    except Reserva.DoesNotExist:
        return Response({"error": "Reserva no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    mesa = reserva.mesa
    mesa.estado = 'Activa'
    mesa.save()

    reserva.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirmar_reserva(request):
    print("Iniciando confirmación de reserva...")

    # Verificar que el usuario tenga el rol de empleado o admin
    if request.user.rol not in ['empleado', 'admin']:
        print("Error: Solo empleados o admins pueden confirmar reservas.")
        return Response({"error": "No tienes permiso para confirmar reservas."}, status=status.HTTP_403_FORBIDDEN)

    reserva_id = request.data.get('reserva_id')

    try:
        reserva = Reserva.objects.get(id=reserva_id)
    except Reserva.DoesNotExist:
        print("Error: Reserva no encontrada.")
        return Response({"error": "Reserva no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    # Cambiar el estado de la reserva a "confirmada"
    reserva.estado = 'confirmada'
    reserva.save()

    # Actualizar el estado de la mesa a "reservada"
    mesa = reserva.mesa
    mesa.estado = 'reservada'
    mesa.save()

    print(f"Reserva ID: {reserva.id} confirmada exitosamente.")
    return Response({"message": "Reserva confirmada exitosamente."}, status=status.HTTP_200_OK)


@receiver(post_save, sender=Reserva)
def crear_factura_si_confirmada(sender, instance, **kwargs):
    if instance.estado == 'Confirmada' and not hasattr(instance, 'factura'):
        Factura.objects.create(
            reserva=instance,
            cliente=instance.cliente,
        )

class UserReservationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Verifica que el rol del usuario no sea empleado o admin
        if user.rol not in ['Empleado', 'admin']:
            # Obtiene la fecha de hoy
            today = timezone.now().date()

            # Filtra todas las reservas donde la fecha sea hoy o en el futuro
            reservas = Reserva.objects.filter(fecha_reserva__gte=today)

            # Serializa las reservas para enviarlas en la respuesta
            serializer = ReservaSerializer(reservas, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

