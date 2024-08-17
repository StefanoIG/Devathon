from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import Factura
from .serializers import FacturaSerializer
from reservas.models import Reserva
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from decimal import Decimal


# Permiso personalizado para permitir solo a empleados y admins
class IsEmpleadoOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.rol == 'empleado' or request.user.is_staff)

class FacturaCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEmpleadoOrAdmin]

    def post(self, request):
        IVA = 0.15  # 15% de IVA

        try:
            reserva = Reserva.objects.get(id=request.data['reserva_id'])
            monto_base = float(request.data['monto_total'])
            monto_con_iva = monto_base * (1 + IVA)
            
            # Crear la factura con el estado 'Pagada'
            factura = Factura.objects.create(
                reserva=reserva,
                cliente=reserva.cliente,
                monto_total=monto_con_iva,
                estado='PAGADA'
            )
            
            # Generar la factura en PDF
            pdf_file = self.generate_pdf(factura)

            # Enviar correo electrónico de confirmación con la factura adjunta
            send_mail(
                subject="Factura generada",
                message=f"Estimado/a {reserva.cliente.nombre}, su factura ha sido generada. Puedes descargarla a continuación, monto total pagado: {monto_con_iva}.",
                from_email="tu_email@dominio.com",
                recipient_list=[reserva.cliente.correo_electronico],
                fail_silently=False,
            )
            
            return Response(FacturaSerializer(factura).data, status=status.HTTP_201_CREATED)
        except Reserva.DoesNotExist:
            return Response({"error": "Reserva no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    

class FacturaDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, reserva_id):
        try:
            factura = Factura.objects.get(reserva__id=reserva_id)
            
            # Verificar si el usuario es cliente y si es el dueño de la factura
            if request.user.rol == 'cliente' and factura.cliente != request.user:
                return Response({"error": "No tienes permiso para acceder a esta factura."}, status=status.HTTP_403_FORBIDDEN)
            
            pdf_buffer = self.generate_pdf(factura)
            return FileResponse(pdf_buffer, as_attachment=True, filename=f"factura_{factura.id}.pdf")
        
        except Factura.DoesNotExist:
            return Response({"error": "Factura no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    def generate_pdf(self, factura):
        # Mismo método de generación de PDF que en FacturaCreateView
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        # Estilo de la tabla
        style = getSampleStyleSheet()
        normal_style = style["Normal"]

        # Calcular los valores
        monto_total = factura.monto_total
        iva_porcentaje = Decimal('0.15')
        precio_sin_iva = monto_total / (1 + iva_porcentaje)
        iva = monto_total * iva_porcentaje

        # Datos para la tabla
        data = [
            ["Factura No:", f"{factura.id}"],
            ["Cliente:", f"{factura.cliente.nombre}"],
            ["Fecha:", f"{factura.fecha_vencimiento.strftime('%d/%m/%Y')}"],
            ["Precio sin IVA:", f"${precio_sin_iva:.2f}"],
            ["Porentaje de iva:", f"15%"],
            ["IVA (15%):", f"${iva:.2f}"],
            ["Precio final:", f"${monto_total:.2f}"],
        ]

        # Crear la tabla
        table = Table(data, colWidths=[2.5 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Añadir la tabla a los elementos del documento
        elements.append(table)

        # Generar el PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer



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
    
class FacturaDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            factura = Factura.objects.get(pk=pk, cliente=request.user)
            factura.delete()
            return Response({"message": "Factura eliminada (soft delete)"}, status=status.HTTP_204_NO_CONTENT)
        except Factura.DoesNotExist:
            return Response({"error": "Factura no encontrada o no tiene permiso para eliminarla"}, status=status.HTTP_404_NOT_FOUND)
