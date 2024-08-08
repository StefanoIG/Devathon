#Vamos a crear url de la api con viewset

from .api import MesaViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('api/v2/mesas', MesaViewSet, 'Mesas')

urlpatterns = router.urls