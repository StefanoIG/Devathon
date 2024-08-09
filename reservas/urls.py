from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import ReservaViewSet

router = DefaultRouter()
router.register(r'api/v1/reservas', ReservaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
