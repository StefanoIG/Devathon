from django.urls import path
from rest_framework.routers import DefaultRouter
from .api import ClienteViewSet
from .views import register,ClienteDetailView, MesasView  # Asegúrate de importar la vista de registro correctamente

router = DefaultRouter()
router.register('api/clientes', ClienteViewSet, 'clientes')

# Combina las rutas del router con las rutas adicionales
urlpatterns = router.urls + [
    path('api/v1/register/', register, name='register'),
    path('api/v1/clientes/', ClienteDetailView.as_view(), name='cliente-detail'),
    path('mesas/', MesasView.as_view(), name='mesas-view'),
    path('mesas/<int:pk>/', MesasView.as_view(), name='mesas-detail'),  # Para PUT y DELETE
]
