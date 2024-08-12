from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import ReservaViewSet
from .views import create_reserva, cancel_reserva

router = DefaultRouter()
router.register(r'reservas', ReservaViewSet)

urlpatterns = [
    path('api/v1/reservaAll/', include(router.urls)),  # Incluye las rutas del ViewSet
    path('api/v1/crear-reserva/', create_reserva, name='crear_reserva'),  # Ruta para la vista de crear reserva
    path('api/v1/cancelar-reserva/<int:pk>/', cancel_reserva, name='cancelar_reserva'),  # Ruta para cancelar reserva
]
