#Crear viewset de Mesa
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Mesa
from .serializers import MesaSerializer
from rest_framework import viewsets


class MesaViewSet(viewsets.ModelViewSet):
    queryset = Mesa.objects.all()
    serializer_class = MesaSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]