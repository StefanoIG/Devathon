from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import make_password
from .models import Cliente
from mesas.models import Mesa
from mesas.serializers import MesaSerializer,ClienteMesaSerializer
from .serializers import ClienteSerializer

# Registrar un nuevo cliente
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    if request.method == 'POST':
        serializer = ClienteSerializer(data=request.data)
        if serializer.is_valid():
            cliente = serializer.save(password=make_password(serializer.validated_data['password']))
            return Response(ClienteSerializer(cliente).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Definición de permisos personalizados
from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.rol == 'admin'

class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.rol == 'user'

class IsEmpleado(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.rol == 'empleado'

# Vista para manejar detalles de clientes con restricciones de acceso basadas en roles
from rest_framework.views import APIView
from rest_framework.response import Response

class ClienteDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.rol == 'admin':
            clientes = Cliente.objects.all()
        elif user.rol == 'empleado':
            clientes = Cliente.objects.values('nombre', 'apellido')
        elif user.rol == 'user':
            clientes = Cliente.objects.filter(id=user.id)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)

# Vista para manejar la información de mesas con restricciones de acceso basadas en roles
class MesasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.rol == 'admin':
            mesas = Mesa.objects.all()
            serializer = MesaSerializer(mesas, many=True)
        elif user.rol == 'empleado':
            mesas = Mesa.objects.all()
            serializer = MesaSerializer(mesas, many=True)
        elif user.rol == 'user':
            mesas = Mesa.objects.all()
            serializer = ClienteMesaSerializer(mesas, many=True)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        return Response(serializer.data)

    def post(self, request):
        if request.user.rol != 'admin':
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        serializer = MesaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if request.user.rol != 'admin':
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        try:
            mesa = Mesa.objects.get(pk=pk)
        except Mesa.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = MesaSerializer(mesa, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.rol != 'admin':
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        try:
            mesa = Mesa.objects.get(pk=pk)
        except Mesa.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        mesa.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)