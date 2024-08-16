from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from .models import Factura
from .serializers import FacturaSerializer
from reservas.models import Reserva

class FacturaCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            reserva = Reserva.objects.get(id=request.data['reserva_id'])
            monto_total = request.data['monto_total']
            
            factura = Factura.objects.create(
                reserva=reserva,
                cliente=reserva.cliente,
                monto_total=monto_total
            )
            
            # Enviar correo electrónico de confirmación
            send_mail(
                subject="Factura creada",
                message=f"Estimado/a {reserva.cliente.nombre}, su factura ha sido creada con un monto total de {monto_total}.",
                from_email="tu_email@dominio.com",
                recipient_list=[reserva.cliente.correo_electronico],
                fail_silently=False,
            )
            
            return Response(FacturaSerializer(factura).data, status=status.HTTP_201_CREATED)
        except Reserva.DoesNotExist:
            return Response({"error": "Reserva no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FacturaDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            factura = Factura.objects.get(pk=pk, cliente=request.user)
            factura.delete()
            return Response({"message": "Factura eliminada (soft delete)"}, status=status.HTTP_204_NO_CONTENT)
        except Factura.DoesNotExist:
            return Response({"error": "Factura no encontrada o no tiene permiso para eliminarla"}, status=status.HTTP_404_NOT_FOUND)


class ClienteFacturasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        facturas = Factura.objects.filter(cliente=request.user, is_active=True)
        serializer = FacturaSerializer(facturas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminFacturasView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        facturas = Factura.objects.filter(is_active=True)
        serializer = FacturaSerializer(facturas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
