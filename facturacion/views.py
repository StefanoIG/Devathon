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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from decimal import Decimal
import os


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
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Datos de la factura
        monto_total = factura.monto_total
        iva_porcentaje = Decimal('0.15')
        precio_sin_iva = monto_total / (1 + iva_porcentaje)
        iva = monto_total * iva_porcentaje

        styles = getSampleStyleSheet()
        header_style = ParagraphStyle(name='Header', fontSize=16, spaceAfter=12, alignment=0)  # Alineación izquierda
        title_style = ParagraphStyle(name='Title', fontSize=12, spaceAfter=8, alignment=0)  # Tamaño de fuente menor
        normal_style = styles["Normal"]

        # Agregar logo de la entidad emisora
        logo_path = os.path.join(os.path.dirname(__file__), 'img', 'logo.png')
        try:
            logo = Image(logo_path)
            logo.drawHeight = 1.5 * inch
            logo.drawWidth = 1.5 * inch
            logo_table = Table([[logo]], colWidths=[1.5 * inch])
            logo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (0, 0), 'TOP')
            ]))
            elements.append(logo_table)
        except:
            pass

        # Encabezado de la factura
        elements.append(Paragraph("Factura", header_style))
        elements.append(Spacer(1, 12))

        # Información de la factura
        data_info = [
            ["De:", "Changarro de Mexacol.", "", "N° de Factura", f"{factura.id}"],
            ["", "Algun lugar del mundo", "", "Fecha de emisión", f"{factura.fecha_vencimiento.strftime('%d/%m/%Y')}"],
            ["", "Hecho con amor <3", "", "", ""],
            ["Facturar a:", f"{factura.cliente.nombre} {factura.cliente.apellido}", "", "Fecha de pago", f"{factura.fecha_vencimiento.strftime('%d/%m/%Y')}"]
        ]
        table_info = Table(data_info, colWidths=[1 * inch, 2.5 * inch, 0.5 * inch, 2 * inch, 2 * inch])
        table_info.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('SPAN', (1, 0), (1, 1)),  # Combina celdas para la dirección
            ('SPAN', (1, 3), (1, 3)),  # Combina celdas para la dirección del cliente
            ('SPAN', (0, 3), (0, 3)),  # Combina celdas para "Facturar a:"
        ]))
        elements.append(table_info)
        elements.append(Spacer(1, 12))

        # Detalles de la factura
        data_detalle = [
            ["CANT.", "DESCRIPCIÓN", "PRECIO UNITARIO", "IMPORTE"],
            ["1", "Consumo de alimentos", f"${monto_total:.2f}", f"${iva:.2f}"],
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "Subtotal", f"${precio_sin_iva:.2f}"],
            ["", "", "IVA 15.0%", f"${iva:.2f}"],
            ["", "", "TOTAL", f"${monto_total:.2f}"]
        ]
        table_detalle = Table(data_detalle, colWidths=[1 * inch, 3 * inch, 2 * inch, 2 * inch])
        table_detalle.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('ALIGN', (2, 0), (-1, 0), 'RIGHT'),  # Alinear encabezados a la derecha
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Alinear precios e importes a la derecha
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        elements.append(table_detalle)
        elements.append(Spacer(1, 24))

        # Tabla de total
        data_total = [["Total", f"${monto_total:.2f}"]]
        table_total = Table(data_total, colWidths=[3.5 * inch, 2 * inch])
        table_total.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('FONTSIZE', (0, 0), (1, 0), 14),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(table_total)
        elements.append(Spacer(1, 24))

        # Condiciones y forma de pago
        elements.append(Paragraph("Condiciones y forma de pago", title_style))
        elements.append(Spacer(1, 1))
        elements.append(Paragraph("Pago en efectivo, tarjeta de crédito o transferencia bancaria.", normal_style))
        elements.append(Paragraph("Pago realizado en el local.", normal_style))
        elements.append(Paragraph("0 días plazo de pago.", normal_style))
        elements.append(Spacer(1, 12))

        # Nota y firma
        elements.append(Paragraph("Gracias por su preferencia. Si tiene alguna pregunta sobre esta factura, no dude en contactarnos.", normal_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Atentamente, el equipo de Changarro de Mexacol.", normal_style))
        elements.append(Spacer(1, 12))

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
