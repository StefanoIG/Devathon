#Vamos a crear url de la api con viewset

from .api import ClienteViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('api/clientes', ClienteViewSet, 'clientes')

urlpatterns = router.urls