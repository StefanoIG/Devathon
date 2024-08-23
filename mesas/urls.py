#Vamos a crear url de la api con viewset

from .api import MesaViewSet
from rest_framework.routers import DefaultRouter
from .views import mesas_libres, mesas_a_estar_libres
from django.urls import path

router = DefaultRouter()

router.register('api/v2/mesas', MesaViewSet, 'Mesas')

urlpatterns = router.urls

# urlpatterns = [
#     path('api/v1/mesas-libres/', mesas_libres, name='mesas_libres'),
#     path('api/v1/mesas-a-estar-libres/', mesas_a_estar_libres, name='mesas_a_estar_libres'),
# ]