from .api import EmpleadoViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('api/empleados', EmpleadoViewSet, 'empleados')

urlpatterns = router.urls