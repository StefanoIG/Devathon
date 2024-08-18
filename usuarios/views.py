from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import make_password
from .models import Cliente
from mesas.models import Mesa
from mesas.serializers import MesaSerializer, ClienteMesaSerializer
from .serializers import ClienteSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework_simplejwt.authentication import JWTAuthentication

# Registrar un nuevo cliente
@extend_schema(
    request=ClienteSerializer,
    responses={201: ClienteSerializer},
    examples=[
        OpenApiExample(
            'Registrar un nuevo cliente',
            summary='Registrar un nuevo cliente',
            description='Registrar un nuevo cliente',
            value={
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'correo_electronico': 'test@test.com',
                'telefono': '1234567890',
                'password': 'password',
                'rol': 'user'
            },
        ),
    ],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    if request.method == 'POST':
        serializer = ClienteSerializer(data=request.data)
        if serializer.is_valid():
            cliente = serializer.save(password=make_password(serializer.validated_data['password']))
            return Response(ClienteSerializer(cliente).data, status=status.HTTP_201_CREATED)
        if serializer.errors.get('correo_electronico') and serializer.errors.get('correo_electronico')==['cliente with this correo electronico already exists.']:
            return Response({'error': 'Correo electrónico ya registrado'}, status=status.HTTP_409_CONFLICT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Iniciar sesión / Login
@extend_schema(
    request=ClienteSerializer,
    responses={
        200: ClienteSerializer, 
        404: 'Correo electrónico o contraseña incorrectos'
        },
    examples=[
        OpenApiExample(
            'Iniciar sesión',
            summary='Iniciar sesión',
            description='Iniciar sesión',
            value={
                'correo_electronico': 'test2@test.com',
                'password': 'prueba',
            },
        ),
    ],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    if request.method == 'POST':
        email = request.data.get('correo_electronico')
        password = request.data.get('password')
        try:
            cliente = Cliente.objects.get(correo_electronico=email)
        except Cliente.DoesNotExist:
            return Response({'error': 'Correo electrónico o contraseña incorrectos'}, status=status.HTTP_404_NOT_FOUND)
        
        if not cliente.check_password(password):
            return Response({'error': 'Correo electrónico o contraseña incorrectos'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(ClienteSerializer(cliente).data, status=status.HTTP_200_OK)

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
    authentication_classes = [JWTAuthentication]

    @extend_schema(
        parameters=[
            OpenApiParameter('id', OpenApiTypes.INT, description='ID del cliente')
        ],
        responses={200: ClienteSerializer},
        examples=[
            OpenApiExample(
                'Obtener detalles de un cliente',
                summary='Obtener detalles de un cliente',
                description='Obtener detalles de un cliente',
                value={
                    "id": 2,
                    "nombre": "andres",
                    "apellido": "test",
                    "telefono": "60333333",
                    "correo_electronico": "test2@test.com",
                    "fecha_registro": "2024-08-05T13:25:23.126112Z"
                },
            ),
        ],
    )
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
            mesas = Mesa.objects.all().values('id', 'estado')
            return Response(mesas)
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
