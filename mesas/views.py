from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Mesa
from reservas.models import Reserva

@api_view(['GET'])
def mesas_libres(request):
    now = timezone.now()
    future_time = now + timedelta(minutes=15)

    # Obtenemos las mesas que tienen reservas activas en los próximos 15 minutos
    mesas_reservadas = Mesa.objects.filter(
        reserva__is_active=True,
        reserva__fecha_reserva=now.date(),
        reserva__hora_reserva__lt=future_time.time(),
        reserva__hora_fin_reserva__gte=now.time()
    ).distinct()

    # Excluir esas mesas de las mesas disponibles
    mesas_libres = Mesa.objects.filter(
        is_activate=True,
        estado='activa'
    ).exclude(
        id__in=mesas_reservadas
    ).order_by('numero').distinct()

    # Paginar mesas libres
    paginator = Paginator(mesas_libres, 10)  # 10 mesas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return Response({
        'mesas_libres': [mesa.numero for mesa in page_obj],
        'page_number': page_obj.number,
        'num_pages': paginator.num_pages
    })

@api_view(['GET'])
def mesas_a_estar_libres(request):
    now = timezone.now()
    future_time = now + timedelta(minutes=15)

    # Filtrar mesas que están ocupadas ahora pero estarán libres en menos de 15 minutos
    mesas_a_estar_libres = Mesa.objects.filter(
        is_activate=True,
        estado='reservada',
        reserva__is_active=True,
        reserva__fecha_reserva=now.date(),
        reserva__hora_reserva__lte=now.time(),
        reserva__hora_fin_reserva__lt=future_time.time()
    ).order_by('numero').distinct()

    # Paginar mesas a estar libres
    paginator = Paginator(mesas_a_estar_libres, 10)  # 10 mesas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return Response({
        'mesas_a_estar_libres': [mesa.numero for mesa in page_obj],
        'page_number': page_obj.number,
        'num_pages': paginator.num_pages
    })
