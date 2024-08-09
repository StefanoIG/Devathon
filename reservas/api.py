from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Reserva
from .serializers import ReservaSerializer

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)

    def destroy(self, request, *args, **kwargs):
        reserva = self.get_object()
        mesa = reserva.mesa
        mesa.estado = 'disponible'
        mesa.save()
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.rol == 'admin':
            return Reserva.objects.all()
        elif user.rol == 'empleado':
            return Reserva.objects.filter(empleado=user) | Reserva.objects.filter(cliente=user)
        elif user.rol == 'user':
            return Reserva.objects.filter(cliente=user)
        else:
            return Reserva.objects.none()
