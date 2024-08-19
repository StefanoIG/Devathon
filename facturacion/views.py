from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.http import FileResponse
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
                #Generar y enviar el archivo PDF de la funcion generate_pdf
                attachment=[pdf_file],
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
        header_style = ParagraphStyle(name='Header', fontSize=16, spaceAfter=12, alignment=1)  # Centered alignment
        title_style = ParagraphStyle(name='Title', fontSize=10, spaceAfter=8, alignment=0)  # Left alignment
        normal_style = styles["Normal"]

        # Logo de la entidad emisora y datos de la factura
        logo_path = os.path.join(os.path.dirname(__file__), 'img', 'logo.png')
        try:
            logo = Image(logo_path)
            logo.drawHeight = 1.5 * inch
            logo.drawWidth = 1.5 * inch
            logo_table = Table([
                [logo, '', Paragraph("<b>N° de Factura:</b>", normal_style), Paragraph(f"{factura.id}", normal_style)],
                ['', '', Paragraph("<b>Fecha de emisión:</b>", normal_style), Paragraph(f"{factura.fecha_vencimiento.strftime('%d/%m/%Y')}", normal_style)],
                ['','',Paragraph("<b>Fecha de vencimiento:</b>", normal_style), Paragraph(f"{factura.fecha_vencimiento.strftime('%d/%m/%Y')}", normal_style)],
                ['','',Paragraph("<b>Estado:</b>", normal_style), Paragraph(f"{factura.estado}", normal_style)],
            ], colWidths=[2 * inch, 2.5 * inch, 1.5 * inch, 1.5 * inch])
            logo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (0, 0), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(logo_table)
        except:
            elements.append(Paragraph("Factura", header_style))
        elements.append(Spacer(1, 12))

        # Información del emisor y receptor
        data_info = [
            [Paragraph("<b>Datos del emisor:</b>", normal_style), '', Paragraph("<b>Datos del receptor:</b>", normal_style)],
            [f"Changarro de Mexacol.\nAlgun lugar del mundo\nHecho con amor <3", '', f"{factura.cliente.nombre} {factura.cliente.apellido}"]
        ]
        table_info = Table(data_info, colWidths=[3 * inch, 1 * inch, 3 * inch])
        table_info.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('SPAN', (1, 0), (1, 1)),  # Empty column for spacing
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
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

        

        # Condiciones y forma de pago, y Nota y firma
        payment_conditions_table = Table(
            [[Paragraph("<b>Condiciones y forma de pago</b>", title_style)],  # Negrita en el título
            [Paragraph("Pago en efectivo, tarjeta de crédito o transferencia bancaria.", normal_style)],
            [Paragraph("Pago realizado en el local.", normal_style)],
            [Paragraph("0 días plazo de pago.", normal_style)]],
            colWidths=[3 * inch])
        payment_conditions_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 16),
        ]))

        note_and_signature_table = Table(
            [[Paragraph("Gracias por su preferencia. Si tiene alguna pregunta sobre esta factura, no dude en contactarnos.", normal_style)],
            [Spacer(1, 12)],
            [Paragraph("Atentamente, el equipo de Changarro de Mexacol.", normal_style)]],
            colWidths=[4.5 * inch])
        note_and_signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 4),
        ]))

        # Secciona las tablas en dos columnas, centradas
        midfooter_table = Table([[payment_conditions_table]], colWidths=[2 * inch, 2.5 * inch])
        midfooter_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(Spacer(1, 20))  # Añade un espacio para bajar la tabla de agradecimiento
        elements.append(midfooter_table)

        # Secciona las tablas en dos columnas, centradas
        footer_table = Table([[note_and_signature_table]], colWidths=[3 * inch, 2.5 * inch])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(Spacer(-2, -10))  # Ajuste de espacio para subir la tabla de agradecimiento
        elements.append(footer_table)

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
