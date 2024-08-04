from django.urls import path
from rest_framework.routers import DefaultRouter
from .api import ClienteViewSet
from .views import register  # Asegúrate de importar la vista de registro correctamente

router = DefaultRouter()
router.register('api/clientes', ClienteViewSet, 'clientes')

# Combina las rutas del router con las rutas adicionales
urlpatterns = router.urls + [
    path('api/register/', register, name='register'),
]
