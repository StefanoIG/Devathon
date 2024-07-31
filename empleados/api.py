from rest_framework import viewsets
from .models import Empleado
from .serializers import EmpleadoSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

