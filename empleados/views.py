from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Empleado
from .serializers import EmpleadoSerializer
from usuarios.views import IsAdminUser, IsEmpleado

class EmpleadoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        user = request.user

        if user.rol == 'admin':
            if pk:
                try:
                    empleado = Empleado.objects.get(pk=pk)
                except Empleado.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                serializer = EmpleadoSerializer(empleado)
            else:
                empleados = Empleado.objects.all()
                serializer = EmpleadoSerializer(empleados, many=True)
        elif user.rol == 'empleado':
            try:
                empleado = Empleado.objects.get(correo_electronico=user.correo_electronico)
            except Empleado.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = EmpleadoSerializer(empleado)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.data)

    def post(self, request):
        if request.user.rol != 'admin':
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = EmpleadoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if request.user.rol != 'admin':
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            empleado = Empleado.objects.get(pk=pk)
        except Empleado.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = EmpleadoSerializer(empleado, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.rol != 'admin':
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            empleado = Empleado.objects.get(pk=pk)
        except Empleado.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        empleado.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
